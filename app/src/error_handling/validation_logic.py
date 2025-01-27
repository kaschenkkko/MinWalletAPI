from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

ERROR_MESSAGES = {
    "uuid_parsing": "Неверный формат UUID для параметра «wallet_uuid».",
    "greater_than_equal": "Поле «amount» не может быть отрицательным числом.",
    "enum": "Поле «operation_type» может содержать только тип 'DEPOSIT' или 'WITHDRAW'.",
    "missing": "Вы должны передать два обязательных поля «amount» и «operation_type».",
    "wallet_not_found": "Кошелек не найден",
    "insufficient_balance": "Недостаточно средств на кошельке",
}


async def standard_validation_exception_handler(request: Request, exc: RequestValidationError):
    """Стандартный обработчик ошибок."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


async def custom_exception_handler(request: Request, exc: RequestValidationError):
    """Кастомный обработчик ошибок."""
    for error in exc.errors():
        if error["type"] in ERROR_MESSAGES:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": ERROR_MESSAGES[error["type"]]}
            )

    return await standard_validation_exception_handler(request, exc)
