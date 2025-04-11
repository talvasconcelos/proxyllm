import pytest
from fastapi import APIRouter
from proxyllm import (  # type: ignore[import]
    proxyllm_ext,
    proxyllm_start,
    proxyllm_stop,
)


@pytest.mark.asyncio
async def test_router():
    # Test if the router can be included without issues
    router = APIRouter()
    router.include_router(proxyllm_ext)


@pytest.mark.asyncio
async def test_start_and_stop():
    # Test the start and stop lifecycle methods
    proxyllm_start()
    # Add assertion to verify start behavior
    assert proxyllm_ext.router is not None

    proxyllm_stop()
    # Add assertion to verify stop behavior
    assert proxyllm_ext.router is None
