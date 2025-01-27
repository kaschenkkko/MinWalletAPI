from uuid import uuid4

import httpx
import pytest
from fastapi import status
from src.error_handling.validation_logic import ERROR_MESSAGES
from src.main import app
from src.models.wallet import Wallet


@pytest.mark.asyncio
async def test_get_empty_wallets():
    async with httpx.AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.get("/api/v1/wallets")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_get_wallets(db):
    new_wallet = Wallet(balance=100)
    db.add(new_wallet)
    await db.commit()

    async with httpx.AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.get("/api/v1/wallets")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_balance(db, mock_redis):
    wallet_uuid = uuid4()
    new_wallet = Wallet(uuid=wallet_uuid, balance=100)

    db.add(new_wallet)
    await db.commit()

    async with httpx.AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.get(f"/api/v1/wallets/{wallet_uuid}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['balance'] == 100


@pytest.mark.asyncio
async def test_get_balance_error_wallet_not_found(mock_redis):
    non_existent_uuid = uuid4()

    async with httpx.AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.get(f"/api/v1/wallets/{non_existent_uuid}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert ERROR_MESSAGES["wallet_not_found"] in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_balance_wallet_error_uuid_parsing(mock_redis):
    non_uuid = "non_uuid"

    async with httpx.AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.get(f"/api/v1/wallets/{non_uuid}")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert ERROR_MESSAGES["uuid_parsing"] in response.json()["detail"]


@pytest.mark.asyncio
async def test_perform_operation_type_withdraw(db, mock_redis):
    wallet_uuid = uuid4()
    new_wallet = Wallet(uuid=wallet_uuid, balance=100)
    db.add(new_wallet)
    await db.commit()

    operation_data = {
        "amount": 50,
        "operation_type": "WITHDRAW"
    }

    async with httpx.AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.post(f"/api/v1/wallets/{wallet_uuid}/operation", json=operation_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['new_balance'] == 50


@pytest.mark.asyncio
async def test_perform_operation_type_deposit(db, mock_redis):
    wallet_uuid = uuid4()
    new_wallet = Wallet(uuid=wallet_uuid, balance=100)
    db.add(new_wallet)
    await db.commit()

    operation_data = {
        "amount": 50,
        "operation_type": "DEPOSIT"
    }

    async with httpx.AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.post(f"/api/v1/wallets/{wallet_uuid}/operation", json=operation_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['new_balance'] == 150


@pytest.mark.asyncio
async def test_perform_operation_error_insufficient_balance(db, mock_redis):
    wallet_uuid = uuid4()
    new_wallet = Wallet(uuid=wallet_uuid, balance=100)
    db.add(new_wallet)
    await db.commit()

    operation_data = {
        "operation_type": "WITHDRAW",
        "amount": 150
    }

    async with httpx.AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.post(f"/api/v1/wallets/{wallet_uuid}/operation", json=operation_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert ERROR_MESSAGES["insufficient_balance"] in response.json()['detail']


@pytest.mark.asyncio
async def test_perform_operation_error_enum(db, mock_redis):
    wallet_uuid = uuid4()
    new_wallet = Wallet(uuid=wallet_uuid, balance=100)
    db.add(new_wallet)
    await db.commit()

    operation_data = {
        "operation_type": "ENUM",
        "amount": 150
    }

    async with httpx.AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.post(f"/api/v1/wallets/{wallet_uuid}/operation", json=operation_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert ERROR_MESSAGES["enum"] in response.json()['detail']


@pytest.mark.asyncio
async def test_perform_operation_error_missing(db, mock_redis):
    wallet_uuid = uuid4()
    new_wallet = Wallet(uuid=wallet_uuid, balance=100)
    db.add(new_wallet)
    await db.commit()

    operation_data = {
        "operation_type": "WITHDRAW"
    }

    async with httpx.AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.post(f"/api/v1/wallets/{wallet_uuid}/operation", json=operation_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert ERROR_MESSAGES["missing"] in response.json()['detail']


@pytest.mark.asyncio
async def test_perform_operation_error_greater_than_equal(db, mock_redis):
    wallet_uuid = uuid4()
    new_wallet = Wallet(uuid=wallet_uuid, balance=200)
    db.add(new_wallet)
    await db.commit()

    operation_data = {
        "operation_type": "DEPOSIT",
        "amount": -150
    }

    async with httpx.AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.post(f"/api/v1/wallets/{wallet_uuid}/operation", json=operation_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert ERROR_MESSAGES["greater_than_equal"] in response.json()['detail']
