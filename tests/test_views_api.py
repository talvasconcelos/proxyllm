import pytest
from httpx import AsyncClient
from proxyllm.models import CreateAgent

from lnbits.core.crud import create_wallet


@pytest.mark.asyncio
async def test_create_agent(client: AsyncClient):
    # Create a wallet
    wallet = await create_wallet(user="user123", admin=True)

    # Create an agent
    agent_data = {
        "wallet_id": wallet.id,
        "name": "Test Agent",
        "api_url": "http://example.com",
        "model_name": "gpt-3.5-turbo",
    }
    response = await client.post(
        "/proxyllm/api/v1/agents",
        json=agent_data,
        headers={"X-Api-Key": wallet.adminkey},
    )
    assert response.status_code == 201
    agent = response.json()
    assert agent["name"] == "Test Agent"
    assert agent["model_name"] == "gpt-3.5-turbo"


@pytest.mark.asyncio
async def test_get_agent(client: AsyncClient):
    # Create a wallet
    wallet = await create_wallet(user="user123", admin=True)

    # Create an agent
    agent_data = {
        "wallet_id": wallet.id,
        "name": "Test Agent",
        "api_url": "http://example.com",
        "model_name": "gpt-3.5-turbo",
    }
    create_response = await client.post(
        "/proxyllm/api/v1/agents",
        json=agent_data,
        headers={"X-Api-Key": wallet.adminkey},
    )
    agent = create_response.json()

    # Fetch the agent
    response = await client.get(
        f"/proxyllm/api/v1/agents/{agent['id']}",
        headers={"X-Api-Key": wallet.adminkey},
    )
    assert response.status_code == 200
    fetched_agent = response.json()
    assert fetched_agent["id"] == agent["id"]
    assert fetched_agent["name"] == "Test Agent"
    assert "id" in fetched_agent
    assert "name" in fetched_agent
    assert "model_name" in fetched_agent


@pytest.mark.asyncio
async def test_update_agent(client: AsyncClient):
    # Create a wallet
    wallet = await create_wallet(user="user123", admin=True)

    # Create an agent
    agent_data = {
        "wallet_id": wallet.id,
        "name": "Test Agent",
        "api_url": "http://example.com",
        "model_name": "gpt-3.5-turbo",
    }
    create_response = await client.post(
        "/proxyllm/api/v1/agents",
        json=agent_data,
        headers={"X-Api-Key": wallet.adminkey},
    )
    agent = create_response.json()

    # Update the agent
    updated_data = {
        "wallet_id": wallet.id,
        "name": "Updated Agent",
        "api_url": "http://example-updated.com",
        "model_name": "gpt-4",
    }
    response = await client.put(
        f"/proxyllm/api/v1/agents/{agent['id']}",
        json=updated_data,
        headers={"X-Api-Key": wallet.adminkey},
    )
    assert response.status_code == 200
    updated_agent = response.json()
    assert updated_agent["name"] == "Updated Agent"
    assert updated_agent["model_name"] == "gpt-4"
    assert "id" in updated_agent
    assert "name" in updated_agent
    assert "model_name" in updated_agent


@pytest.mark.asyncio
async def test_delete_agent(client: AsyncClient):
    # Create a wallet
    wallet = await create_wallet(user="user123", admin=True)

    # Create an agent
    agent_data = {
        "wallet_id": wallet.id,
        "name": "Test Agent",
        "api_url": "http://example.com",
        "model_name": "gpt-3.5-turbo",
    }
    create_response = await client.post(
        "/proxyllm/api/v1/agents",
        json=agent_data,
        headers={"X-Api-Key": wallet.adminkey},
    )
    agent = create_response.json()

    # Delete the agent
    response = await client.delete(
        f"/proxyllm/api/v1/agents/{agent['id']}",
        headers={"X-Api-Key": wallet.adminkey},
    )
    assert response.status_code == 204

    # Verify the agent is deleted
    get_response = await client.get(
        f"/proxyllm/api/v1/agents/{agent['id']}",
        headers={"X-Api-Key": wallet.adminkey},
    )
    assert get_response.status_code == 404
