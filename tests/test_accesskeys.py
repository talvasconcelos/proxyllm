import pytest
from httpx import AsyncClient
from proxyllm.models import AccessKeyRequest

from lnbits.core.crud import create_wallet


@pytest.mark.asyncio
async def test_create_access_key(client: AsyncClient):
    # Create a wallet
    wallet = await create_wallet(user="user123", admin=True)

    # Create an agent
    agent_data = {
        "wallet_id": wallet.id,
        "name": "Test Agent",
        "api_url": "http://example.com",
        "model_name": "gpt-3.5-turbo",
    }
    agent_response = await client.post(
        "/proxyllm/api/v1/agents",
        json=agent_data,
        headers={"X-Api-Key": wallet.adminkey},
    )
    agent = agent_response.json()

    # Request an access key
    access_key_data = {
        "uses": 10,
        "unit_type": "request",
    }
    response = await client.post(
        f"/proxyllm/api/v1/agents/{agent['id']}/invoice",
        json=access_key_data,
    )
    assert response.status_code == 201
    access_key = response.json()
    assert access_key["uses"] == 10
    assert access_key["unit_type"] == "request"
    assert "id" in access_key
    assert "uses" in access_key
    assert "unit_type" in access_key


@pytest.mark.asyncio
async def test_get_access_keys(client: AsyncClient):
    # Create a wallet
    wallet = await create_wallet(user="user123", admin=True)

    # Fetch access keys
    response = await client.get(
        "/proxyllm/api/v1/accesskeys",
        headers={"X-Api-Key": wallet.adminkey},
    )
    assert response.status_code == 200
    access_keys = response.json()
    assert isinstance(access_keys, list)


@pytest.mark.asyncio
async def test_get_access_key_by_id(client: AsyncClient):
    # Create a wallet
    wallet = await create_wallet(user="user123", admin=True)

    # Create an agent
    agent_data = {
        "wallet_id": wallet.id,
        "name": "Test Agent",
        "api_url": "http://example.com",
        "model_name": "gpt-3.5-turbo",
    }
    agent_response = await client.post(
        "/proxyllm/api/v1/agents",
        json=agent_data,
        headers={"X-Api-Key": wallet.adminkey},
    )
    agent = agent_response.json()

    # Request an access key
    access_key_data = {
        "uses": 10,
        "unit_type": "request",
    }
    key_response = await client.post(
        f"/proxyllm/api/v1/agents/{agent['id']}/invoice",
        json=access_key_data,
    )
    access_key = key_response.json()

    # Fetch the access key by ID
    response = await client.get(
        f"/proxyllm/api/v1/accesskeys/{access_key['id']}",
        headers={"X-Api-Key": wallet.adminkey},
    )
    assert response.status_code == 200
    fetched_key = response.json()
    assert fetched_key["id"] == access_key["id"]
    assert fetched_key["uses"] == 10
    assert "id" in fetched_key
    assert "uses" in fetched_key
    assert "unit_type" in fetched_key
