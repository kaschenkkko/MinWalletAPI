import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.wallet import Wallet

logger = logging.getLogger(__name__)


async def get_all_wallets(
        db: AsyncSession
) -> List[Wallet]:
    """Получаем все объекты «Wallet» из БД."""
    result = await db.execute(select(Wallet).order_by(desc(Wallet.id)))
    wallets = result.scalars().all()
    return wallets


async def get_wallet_by_uuid(
        db: AsyncSession,
        uuid: UUID
) -> Optional[Wallet]:
    """Получаем кошелек из БД, по полю «uuid»."""
    wallet = await db.execute(select(Wallet).filter(Wallet.uuid == uuid))
    return wallet.scalars().one_or_none()


async def change_wallet_balance(
        db: AsyncSession,
        wallet: Wallet,
        operation_type: str,
        amount: int
) -> None:
    """Изменяем баланс кошелька в БД."""
    if operation_type == "DEPOSIT":
        wallet.balance += amount
    elif operation_type == "WITHDRAW":
        wallet.balance -= amount

    await db.commit()
    await db.refresh(wallet)
