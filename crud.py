from typing import List, Optional, Union

from lnbits.db import Database
from lnbits.helpers import create_access_token, urlsafe_short_hash

from .models import (
    AccessKeyRequest,
    Agent,
    AgentAccessKey,
    AgentUsageLog,
    CreateAgent,
    CreateAgentUsageLog,
    PublicAgent,
)

db = Database("ext_proxyllm")


async def get_agents(wallet_ids: Union[str, List[str]]) -> List[Agent]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    q = ",".join([f"'{wallet_id}'" for wallet_id in wallet_ids])
    agents = await db.fetchall(
        f"SELECT * FROM proxyllm.agents WHERE wallet_id IN ({q})",
        model=Agent,
    )
    return agents


async def get_all_agents() -> List[PublicAgent]:
    agents = await db.fetchall("SELECT * FROM proxyllm.agents", model=PublicAgent)
    return agents


async def create_agent(data: CreateAgent) -> Agent:
    agent_id = urlsafe_short_hash()
    agent = Agent(
        id=agent_id,
        **data.dict(),
    )
    await db.insert("proxyllm.agents", agent)
    return agent


async def get_agent(agent_id: str) -> Optional[Agent]:
    agent = await db.fetchone(
        "SELECT * FROM proxyllm.agents WHERE id = :id", {"id": agent_id}, Agent
    )
    return agent


async def update_agent(agent: Agent) -> Agent:
    await db.update("proxyllm.agents", agent)
    return agent


async def delete_agent(agent_id: str) -> None:
    await db.execute("DELETE FROM proxyllm.agents WHERE id = :id", {"id": agent_id})


# Access Keys
async def get_access_keys(agent_ids: Union[str, List[str]]) -> List[AgentAccessKey]:
    if isinstance(agent_ids, str):
        agent_ids = [agent_ids]

    q = ",".join([f"'{agent_id}'" for agent_id in agent_ids])
    access_keys = await db.fetchall(
        f"SELECT * FROM proxyllm.access_keys WHERE agent_id IN ({q})",
        model=AgentAccessKey,
    )
    return access_keys


async def create_access_key(agent_id: str, data: AccessKeyRequest) -> AgentAccessKey:
    if not data.payment_hash:
        raise ValueError("Payment hash is required")
    key_id = urlsafe_short_hash()
    api_key = create_access_token(
        {
            "agent_id": agent_id,
            "access_key_id": key_id,
        }
    )
    access_key = AgentAccessKey(
        id=key_id,
        agent_id=agent_id,
        api_key=api_key,
        payment_hash=data.payment_hash,
        prepaid_units=data.units,
    )
    await db.insert("proxyllm.access_keys", access_key)
    return access_key


async def get_access_key_by_payment_hash(
    payment_hash: str,
) -> Optional[AgentAccessKey]:
    access_key = await db.fetchone(
        "SELECT * FROM proxyllm.access_keys WHERE payment_hash = :payment_hash",
        {"payment_hash": payment_hash},
        AgentAccessKey,
    )
    return access_key


async def get_access_key_by_api_key(api_key: str) -> Optional[AgentAccessKey]:
    access_key = await db.fetchone(
        "SELECT * FROM proxyllm.access_keys WHERE api_key = :api_key",
        {"api_key": api_key},
        AgentAccessKey,
    )
    return access_key


async def get_access_key(access_key_id: str) -> Optional[AgentAccessKey]:
    access_key = await db.fetchone(
        "SELECT * FROM proxyllm.access_keys WHERE id = :id",
        {"id": access_key_id},
        AgentAccessKey,
    )
    return access_key


async def update_access_key(access_key: AgentAccessKey) -> AgentAccessKey:
    await db.update("proxyllm.access_keys", access_key)
    return access_key


# Usage Logs
async def create_usage_log(data: CreateAgentUsageLog) -> AgentUsageLog:
    log_id = urlsafe_short_hash()
    usage_log = AgentUsageLog(
        id=log_id,
        **data.dict(),
    )
    await db.insert("proxyllm.usage_logs", usage_log)
    return usage_log
