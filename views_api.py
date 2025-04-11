from http import HTTPStatus

from fastapi import APIRouter, Depends, Query
from starlette.exceptions import HTTPException

from lnbits.core.crud import get_user
from lnbits.decorators import WalletTypeInfo, require_admin_key

from .crud import (
    create_agent,
    delete_agent,
    get_access_key,
    get_access_keys,
    get_agent,
    get_agents,
    update_agent,
)
from .models import AccessKeyRequest, AccessKeyResponse, Agent, CreateAgent
from .services import request_access_key

proxyllm_api_router = APIRouter()


@proxyllm_api_router.get("/api/v1/agents")
async def api_agents(
    all_wallets: bool = Query(False),
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    wallet_ids = [wallet.wallet.id]

    if all_wallets:
        user = await get_user(wallet.wallet.user)
        wallet_ids = user.wallet_ids if user else []

    return await get_agents(wallet_ids)


@proxyllm_api_router.get("/api/v1/agents/{agent_id}")
async def api_agent(agent_id: str) -> Agent:
    agent = await get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Agent does not exist."
        )
    return agent


@proxyllm_api_router.post("/api/v1/agents", status_code=HTTPStatus.CREATED)
async def api_agent_create(
    data: CreateAgent, key_type: WalletTypeInfo = Depends(require_admin_key)
):
    if data.wallet_id != key_type.wallet.id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Not your wallet.")
    agent = await create_agent(data=data)
    return agent


@proxyllm_api_router.put("/api/v1/agents/{agent_id}")
async def api_agent_update(
    data: CreateAgent,
    agent_id: str,
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    agent = await get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Agent does not exist."
        )
    if agent.wallet_id != wallet.wallet.id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Not your agent.")
    for key, value in data.dict().items():
        setattr(agent, key, value)
    await update_agent(agent)
    return agent


@proxyllm_api_router.delete("/api/v1/agents/{agent_id}")
async def api_agent_delete(
    agent_id: str, wallet: WalletTypeInfo = Depends(require_admin_key)
):
    agent = await get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Agent does not exist."
        )

    if agent.wallet_id != wallet.wallet.id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Not your agent.")

    await delete_agent(agent_id)

    return "", HTTPStatus.NO_CONTENT


## Access Keys
@proxyllm_api_router.get("/api/v1/accesskeys")
async def api_accesskeys(
    all_wallets: bool = Query(False),
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    wallet_ids = [wallet.wallet.id]
    access_keys = []

    if all_wallets:
        user = await get_user(wallet.wallet.user)
        wallet_ids = user.wallet_ids if user else []
        # get all agents for all wallets
        agents = await get_agents(wallet_ids)
        agent_ids = [agent.id for agent in agents]
        access_keys = await get_access_keys(agent_ids)

    return access_keys


@proxyllm_api_router.post(
    "/api/v1/agents/{agent_id}/invoice", status_code=HTTPStatus.CREATED
)
async def api_agent_invoice(agent_id: str, data: AccessKeyRequest) -> AccessKeyResponse:
    return await request_access_key(agent_id, data)


@proxyllm_api_router.get("/api/v1/accesskeys/{key_id}")
async def api_accesskey(key_id: str):
    access_key = await get_access_key(key_id)
    if not access_key:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Access key does not exist."
        )
    return access_key
