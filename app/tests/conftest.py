import asyncio
from unittest.mock import AsyncMock

import pytest
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from src.database.db_session import Base, get_db
from src.main import app
from src.redis.redis_utils import cache


class SettingsTestDB(BaseSettings):
    """Настройки тестовой БД."""
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    TEST_DB_HOST: str

    @property
    def test_database_url_asyncpg(self):
        """URL для асинхронного подключения к тестовой БД."""
        return (
            f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}'
            f'@{self.TEST_DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )

    class Config:
        env_file = '.env'


db_settings = SettingsTestDB()


async_engine: AsyncEngine = create_async_engine(
    url=db_settings.test_database_url_asyncpg,
    poolclass=NullPool,
)

async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    """Функция для переопределения зависимости get_db."""
    async with async_session() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope='session')
def event_loop():
    """Overrides pytest default function scoped event loop.

    Переопределяем чтобы не было ошибки с фикстурой «setup_database».
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='function')
async def db():
    """Фикстура для предоставления сессии с БД в тестах."""
    async with async_session() as session:
        yield session


@pytest.fixture(scope='session', autouse=True)
async def setup_database():
    """Фикстура для настройки БД перед всеми тестами и очистки после выполнения тестов."""
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='function')
async def mock_redis():
    """Фикстура для мокирования взаимодействия с Redis в тестах."""
    cache.redis = AsyncMock()
    cache.redis.get.return_value = None
    cache.redis.set.return_value = True
    cache.redis.delete.return_value = True
    yield
    cache.redis.reset_mock()
