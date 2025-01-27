from uuid import UUID

import aioredis
from src.redis.redis_config import settings_redis


class RedisCache:
    """Класс для работы с кэшем Redis."""
    def __init__(self):
        self.redis = None

    async def connect(self):
        """Устанавливаем подключение к Redis серверу и создаем пул соединений."""
        self.redis = await aioredis.create_redis_pool(
            settings_redis.redis_url,
            minsize=5,
            maxsize=10
        )

    async def close(self):
        """Закрываем соединение с Redis сервером и ожидаем завершения закрытия всех соединений."""
        self.redis.close()
        await self.redis.wait_closed()

    async def set_balance_in_cache(self, wallet_uuid: UUID, balance: int):
        """Кэшируем баланс кошелька в Redis."""
        await self.redis.set(str(wallet_uuid), balance)

    async def get_balance_from_cache(self, wallet_uuid: UUID):
        """Получаем баланс кошелька из Redis."""
        cached_balance = await self.redis.get(str(wallet_uuid))
        if cached_balance:
            return int(cached_balance)
        return None

    async def clear_balance_cache(self, wallet_uuid: UUID):
        """Очистка кэша."""
        await self.redis.delete(str(wallet_uuid))


cache = RedisCache()
