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
async def test_get_agents(client: AsyncClient):
    # Create a wallet
    wallet = await create_wallet(user="user123", admin=True)

    # Fetch agents
    response = await client.get(
        "/proxyllm/api/v1/agents",
        headers={"X-Api-Key": wallet.adminkey},
    )
    assert response.status_code == 200
    agents = response.json()
    assert isinstance(agents, list)
    for agent in agents:
        assert "id" in agent
        assert "name" in agent
        assert "model_name" in agent


@pytest.mark.asyncio
async def test_generate_completion(client: AsyncClient):
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

    # Generate a completion
    completion_data = {
        "messages": [{"role": "user", "content": "Hello, how are you?"}],
    }
    response = await client.post(
        f"/proxyllm/openai/v1/chat/completions",
        json=completion_data,
        headers={"Authorization": f"Bearer {agent['id']}"},
    )
    assert response.status_code == 200
    completion = response.json()
    assert "choices" in completion
    assert isinstance(completion["choices"], list)
    for choice in completion["choices"]:
        assert "message" in choice
        assert "content" in choice["message"]
