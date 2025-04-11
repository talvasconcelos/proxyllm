import asyncio

from loguru import logger

from lnbits.core.models import Payment
from lnbits.helpers import get_current_extension_name
from lnbits.tasks import register_invoice_listener

from .services import activate_access_key


async def wait_for_paid_invoices():
    invoice_queue = asyncio.Queue()
    register_invoice_listener(invoice_queue, get_current_extension_name())

    while True:
        payment = await invoice_queue.get()
        await on_invoice_paid(payment)


async def on_invoice_paid(payment: Payment) -> None:
    if not payment.extra or payment.extra.get("tag") != "proxyllm":
        return
    try:
        logger.debug(
            f"ProxyLLM payment received: '{payment.payment_hash}: {payment.memo}'"
        )
        await activate_access_key(payment)
    except Exception as e:
        logger.warning(f"Error processing payment: {e}")
