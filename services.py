import hashlib

from loguru import logger

from lnbits.core.models import Payment
from lnbits.core.services import create_invoice

from .crud import (
    create_access_key,
    create_usage_log,
    get_access_key_by_payment_hash,
    get_agent,
    update_access_key,
)
from .models import (
    AccessKeyRequest,
    AccessKeyResponse,
    AgentAccessKey,
    AgentUsageLog,
    CreateAgentUsageLog,
)


async def request_access_key(
    agent_id: str, data: AccessKeyRequest
) -> AccessKeyResponse:
    agent = await get_agent(agent_id)
    if not agent:
        raise ValueError("Agent not found")

    if data.units < 1:
        raise ValueError("Units must be greater than 0")

    # Create an invoice for the access key
    invoice: Payment = await create_invoice(
        wallet_id=agent.wallet_id,
        amount=data.units * agent.price_per_unit,
        memo=f"Access key for {agent.name}",
        extra={"tag": "proxyllm", "agent_id": agent.id},
    )
    data.payment_hash = invoice.payment_hash
    if agent.unit_type == "token":
        data.units = data.units * 1000

    access_key: AgentAccessKey = await create_access_key(agent_id, data)
    return AccessKeyResponse(
        id=access_key.id,
        payment_hash=access_key.payment_hash,
        payment_request=invoice.bolt11,
    )


async def activate_access_key(payment: Payment) -> bool:
    key = await get_access_key_by_payment_hash(payment.payment_hash)
    if not key:
        logger.warning(f"Access key not found for payment: {payment.payment_hash}")
        return False

    await update_access_key(access_key=key.copy(update={"active": True}))
    logger.debug(f"Access key activated: {key.id} for payment: {payment.payment_hash}")
    return True


async def update_access_key_usage(
    access_key: AgentAccessKey, units_used: int
) -> AgentAccessKey:
    if not access_key.has_uses_left():
        raise ValueError("No more uses left")
    access_key.used_units += units_used
    await update_access_key(access_key)
    return access_key


async def create_log(
    access_key: AgentAccessKey, input_data: str, units_used: int
) -> AgentUsageLog:
    usage_log = CreateAgentUsageLog(
        access_key_id=access_key.id,
        agent_id=access_key.agent_id,
        units_used=units_used,
        input_hash=hashlib.sha256(input_data.encode()).hexdigest(),
    )

    return await create_usage_log(usage_log)
