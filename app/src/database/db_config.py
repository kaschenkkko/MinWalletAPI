from pydantic_settings import BaseSettings


class SettingsDB(BaseSettings):
    """Настройки БД."""
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    @property
    def database_url_asyncpg(self):
        """URL для асинхронного подключения к БД PostgreSQL."""
        return (
            f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}'
            f'@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )

    class Config:
        env_file = '.env'


db_settings = SettingsDB()
