from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.orm import declarative_base, sessionmaker
from src.database.db_config import db_settings

Base = declarative_base()

async_engine: AsyncEngine = create_async_engine(
    url=db_settings.database_url_asyncpg,
    pool_size=20,
    max_overflow=10,
)

async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session
