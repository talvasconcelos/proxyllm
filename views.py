from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.requests import Request

from lnbits.core.models import User
from lnbits.decorators import check_user_exists, optional_user_id
from lnbits.helpers import template_renderer

from .crud import get_access_key_by_api_key, get_agent, get_all_agents

proxyllm_generic_router = APIRouter()


def proxyllm_renderer():
    return template_renderer(["proxyllm/templates"])


@proxyllm_generic_router.get("/")
async def agents_index(
    request: Request,
    user_id: Optional[str] = Depends(optional_user_id),
):
    agents = await get_all_agents()
    return proxyllm_renderer().TemplateResponse(
        "proxyllm/list.html",
        {
            "request": request,
            "is_user_authenticated": user_id is not None,
            "agents": [agent.json() for agent in agents],
        },
    )


@proxyllm_generic_router.get("/admin")
async def index(
    request: Request,
    user: User = Depends(check_user_exists),
):
    return proxyllm_renderer().TemplateResponse(
        "proxyllm/index.html", {"request": request, "user": user.json()}
    )


@proxyllm_generic_router.get("/accesskey/{api_key}")
async def access_key(
    request: Request,
    api_key: str,
):
    access_key = await get_access_key_by_api_key(api_key)
    if not access_key:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Access key does not exist."
        )

    return proxyllm_renderer().TemplateResponse(
        "proxyllm/accesskey.html",
        {
            "request": request,
            "access_key": access_key.json(),
        },
    )


# @proxyllm_generic_router.get("/pay/{link_id}")
# async def pay(
#     request: Request,
#     link_id: str,
# ):
#     print("#### LINK", link_id)
#     link = await get_link(link_id)
#     print(link)
#     if not link:
#         raise HTTPException(
#             status_code=HTTPStatus.NOT_FOUND, detail="Link does not exist."
#         )
#     return proxyllm_renderer().TemplateResponse(
#         "proxyllm/display.html",
#         {
#             "request": request,
#             "link_id": link.id,
#             "description": link.description,
#             "cost": link.cost,
#         },
#     )


# @proxyllm_generic_router.get("/user/{user_id}")
# async def user_page(user_id: str, request: Request):
#     user = await get_proxyllm_user(user_id)
#     if not user:
#         raise HTTPException(
#             status_code=HTTPStatus.NOT_FOUND, detail="User does not exist."
#         )
#     return proxyllm_renderer().TemplateResponse(
#         "proxyllm/user.html", {"request": request, "user": user.json()}
#     )
