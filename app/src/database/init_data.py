import logging
import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.wallet import Wallet

logger = logging.getLogger(__name__)


async def create_initial_wallets(db: AsyncSession,):
    """Добавляем объекты «Wallet» в БД."""
    result = await db.execute(select(Wallet))
    wallets = result.scalars().all()

    if not wallets:
        wallets_to_add = []

        for _ in range(15):
            balance = random.randint(100, 999999)
            wallets_to_add.append(Wallet(balance=balance))

        db.add_all(wallets_to_add)
        await db.commit()
        logger.info("Начальные данные добавлены в БД.")
    else:
        logger.info("Данные в БД присутствуют.")
