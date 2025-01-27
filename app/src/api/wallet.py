import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.wallet import (change_wallet_balance, get_all_wallets,
                             get_wallet_by_uuid)
from src.database.db_session import get_db
from src.error_handling.handler import ErrorHandler
from src.models.wallet import Wallet
from src.redis.redis_utils import cache
from src.schemas.wallet import (BalanceSchema, OperationResponseSchema,
                                OperationSchema, WalletSchema)

logger = logging.getLogger(__name__)

wallet_router = APIRouter()


@wallet_router.get('/api/v1/wallets',
                   response_model=List[WalletSchema],
                   status_code=status.HTTP_200_OK,
                   summary='Получить список кошельков')
async def get_wallets(
    db: AsyncSession = Depends(get_db)
) -> List[Wallet]:
    """
    Получить список всех кошельков в системе.

    Этот эндпоинт позволяет получить информацию о всех кошельках,
    хранящихся в базе данных.
    """
    return await get_all_wallets(db)


@wallet_router.get('/api/v1/wallets/{wallet_uuid}',
                   response_model=BalanceSchema,
                   status_code=status.HTTP_200_OK,
                   summary='Получить баланс кошелька по его UUID')
async def get_balance(
    db: AsyncSession = Depends(get_db),
    wallet_uuid: UUID = Path(..., description='UUID кошелька'),
) -> BalanceSchema:
    """
    Получить баланс кошелька по его UUID.

    Если баланс кошелька найден в кэше Redis, он будет возвращён оттуда,
    иначе баланс будет загружен из базы данных и закэширован.
    """
    balance = await cache.get_balance_from_cache(wallet_uuid)
    if balance:
        logger.info(f"Получаем баланс кошелька '{wallet_uuid}' из Redis.")
        return BalanceSchema(balance=balance)

    wallet: Optional[Wallet] = await get_wallet_by_uuid(db, wallet_uuid)

    if not wallet:
        ErrorHandler.wallet_not_found()

    await cache.set_balance_in_cache(wallet_uuid, wallet.balance)
    logger.info(f"Кэшируем баланс кошелька '{wallet_uuid}'.")

    return BalanceSchema(balance=wallet.balance)


@wallet_router.post('/api/v1/wallets/{wallet_uuid}/operation',
                    response_model=OperationResponseSchema,
                    status_code=status.HTTP_200_OK,
                    summary='Изменить баланс кошелька')
async def perform_operation(
    input_data: OperationSchema,
    db: AsyncSession = Depends(get_db),
    wallet_uuid: UUID = Path(..., description='UUID кошелька'),
) -> OperationResponseSchema:
    """
    Выполнить операцию снятие или пополнения с кошелька.

    Этот эндпоинт позволяет изменять баланс кошелька, например,
    для операций пополнения или снятия средств.
    """
    wallet: Optional[Wallet] = await get_wallet_by_uuid(db, wallet_uuid)

    if not wallet:
        ErrorHandler.wallet_not_found()

    if input_data.operation_type == "WITHDRAW" and wallet.balance < input_data.amount:
        ErrorHandler.insufficient_balance()

    await change_wallet_balance(db, wallet, input_data.operation_type, input_data.amount)

    await cache.clear_balance_cache(wallet_uuid)
    logger.info(f"Кэш кошелька '{wallet_uuid}' очищен.")

    return OperationResponseSchema(new_balance=wallet.balance)
