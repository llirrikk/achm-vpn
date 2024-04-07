from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.routers.api.nodes import get_all_networks, get_all_nodes

pages_router = APIRouter(prefix="", tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


@pages_router.get("/")
async def get_base_page(request: Request):
    """redirect to /nodes"""
    return RedirectResponse(url="/nodes")


@pages_router.get("/nodes")
async def get_all_nodes_page(
    request: Request,
    nodes=Depends(get_all_nodes),
):
    return templates.TemplateResponse(
        "nodes.html", {"request": request, "nodes": nodes}
    )


@pages_router.get("/create_node")
async def get_create_node_page(request: Request):
    return templates.TemplateResponse("create_node.html", {"request": request})


@pages_router.get("/setup")
async def get_setup_page(request: Request):
    return templates.TemplateResponse("setup.html", {"request": request})


@pages_router.get("/networks")
async def get_networks_page(
    request: Request,
    networks=Depends(get_all_networks),
):
    return templates.TemplateResponse(
        "networks.html", {"request": request, "networks": networks}
    )
