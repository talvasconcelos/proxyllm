from http import HTTPStatus

import jwt
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from openai import AsyncOpenAI
from starlette.exceptions import HTTPException

from lnbits.settings import settings

from .crud import (
    get_access_key,
    get_agent,
)
from .models import (
    AccessTokenPayload,
    AgentAccessKey,
    AgentCompletionRequest,
)
from .services import create_log, update_access_key_usage

proxyllm_llm_router = APIRouter(prefix="/openai/v1")

security = HTTPBearer()


def _extract_token_payload(token: str) -> AccessTokenPayload:
    try:
        payload: dict = jwt.decode(token, settings.auth_secret_key, ["HS256"])
        return AccessTokenPayload(**payload)
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid token."
        ) from None


def _run_access_checks(access_key: AgentAccessKey):
    if not access_key.active:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Access key not activated."
        )
    if not access_key.has_uses_left():
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="No more uses left."
        )


@proxyllm_llm_router.get("/models")
async def api_agent_models(
    auth: HTTPAuthorizationCredentials = Depends(security),
):
    if not auth.credentials:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="No API key provided."
        )
    payload = _extract_token_payload(auth.credentials)

    access_key = await get_access_key(payload.access_key_id)
    if not access_key:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid API key."
        )
    _run_access_checks(access_key)

    agent = await get_agent(payload.agent_id)
    if not agent:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Agent does not exist."
        )
    if not agent:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Agent does not exist."
        )
    return {
        "object": "list",
        "data": [
            {
                "id": agent.model_name,
                "object": "model",
            }
        ],
    }


@proxyllm_llm_router.post("/chat/completions")
async def api_agent_generate(
    data: AgentCompletionRequest,
    auth: HTTPAuthorizationCredentials = Depends(security),
):
    if not auth.credentials:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="No API key provided."
        )
    payload = _extract_token_payload(auth.credentials)
    access_key = await get_access_key(payload.access_key_id)
    if not access_key:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid API key."
        )

    _run_access_checks(access_key)

    agent = await get_agent(payload.agent_id)
    if not agent:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Agent does not exist."
        )

    client = AsyncOpenAI(
        base_url=f"{agent.api_url}",
        api_key=agent.api_key if agent.api_key else "NA",
    )

    response = await client.chat.completions.create(
        stream=False,
        model=agent.model_name,
        messages=[
            {"role": msg["role"], "content": msg["content"]} for msg in data.messages
        ],
    )
    if not response:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="No response from the agent.",
        )
    logger.debug(f"### Request : {data.messages}")
    # logger.debug(f"### Response : {response}")
    logger.debug(f"### String Response: {response.choices[0].message.content}")

    units_used = (
        1
        if agent.unit_type == "request"
        else (response.usage.total_tokens if response.usage else 0)
    )

    await update_access_key_usage(access_key, units_used)
    # Create usage log
    await create_log(access_key, f"{response.choices[0].message.content}", units_used)

    return response
