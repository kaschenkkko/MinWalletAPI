from fastapi import HTTPException, status
from src.error_handling.validation_logic import ERROR_MESSAGES


class ErrorHandler:
    """Класс для обработки ошибок."""

    @staticmethod
    def wallet_not_found():
        """Возвращает исключение HTTP 404 (Not Found), если кошелёк не найден."""
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["wallet_not_found"]
        )

    @staticmethod
    def insufficient_balance():
        """Возвращает иисключение HTTP 400 (Bad Request), если баланс кошелька недостаточен."""
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES["insufficient_balance"]
        )
