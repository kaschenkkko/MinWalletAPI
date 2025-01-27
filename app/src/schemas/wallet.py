from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class BalanceSchema(BaseModel):
    balance: int = Field(description='Баланс кошелька')


class WalletSchema(BaseModel):
    id: int = Field(description='ID кошелька')
    uuid: UUID = Field(description='UUID кошелька')
    balance: int = Field(description='Баланс кошелька')


class OperationSchema(BaseModel):
    amount: int = Field(ge=0, description='Сумма для изменения')
    operation_type: OperationType = Field(description='Тип операции')


class OperationResponseSchema(BaseModel):
    new_balance: int = Field(description='Измененный баланс кошелька')
