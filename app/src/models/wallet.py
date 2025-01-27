import uuid

from sqlalchemy import Column, Integer
from sqlalchemy.dialects.postgresql import UUID
from src.database.db_session import Base


class Wallet(Base):
    __tablename__ = 'wallets'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, index=True, unique=True, nullable=False)
    balance = Column(Integer, nullable=False, default=0)
