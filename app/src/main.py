from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from src.api.wallet import wallet_router
from src.database.db_session import async_session
from src.database.init_data import create_initial_wallets
from src.error_handling.validation_logic import custom_exception_handler
from src.logs.logging_config import setup_logging
from src.redis.redis_utils import cache

ERROR_HANDLING_ENABLED = True

setup_logging()


async def lifespan(app):
    async with async_session() as db:
        await create_initial_wallets(db)
    await cache.connect()
    yield
    await cache.close()


app = FastAPI(
    title='Minimal Wallet API',
    description='Минимальный REST API сервис для изменения баланса кошелька.',
    lifespan=lifespan,
)

app.include_router(wallet_router)

if ERROR_HANDLING_ENABLED:
    app.add_exception_handler(RequestValidationError, custom_exception_handler)
