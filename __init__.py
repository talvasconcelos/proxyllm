import asyncio

from fastapi import APIRouter
from loguru import logger

from .crud import db
from .tasks import wait_for_paid_invoices
from .views import proxyllm_generic_router
from .views_api import proxyllm_api_router
from .views_llm import proxyllm_llm_router

proxyllm_ext: APIRouter = APIRouter(prefix="/proxyllm", tags=["ProxyLLM"])
proxyllm_ext.include_router(proxyllm_generic_router)
proxyllm_ext.include_router(proxyllm_api_router)
proxyllm_ext.include_router(proxyllm_llm_router)

proxyllm_static_files = [
    {
        "path": "/proxyllm/static",
        "name": "proxyllm_static",
    }
]
scheduled_tasks: list[asyncio.Task] = []


def proxyllm_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)


def proxyllm_start():
    from lnbits.tasks import create_permanent_unique_task

    task = create_permanent_unique_task("ext_proxyllm", wait_for_paid_invoices)
    scheduled_tasks.append(task)


__all__ = [
    "db",
    "proxyllm_ext",
    "proxyllm_static_files",
    "proxyllm_start",
    "proxyllm_stop",
]
