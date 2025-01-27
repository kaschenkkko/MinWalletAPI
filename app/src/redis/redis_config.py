from pydantic_settings import BaseSettings


class SettingsRedis(BaseSettings):
    """Настройки Redis."""
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int = 0

    @property
    def redis_url(self):
        """URL для подключения к Redis."""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = '.env'


settings_redis = SettingsRedis()
