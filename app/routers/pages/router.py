from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from app.routers.nodes import get_all_nodes

pages_router = APIRouter(prefix="/pages", tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


@pages_router.get("/base")
async def get_base_page(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@pages_router.get("/all_nodes")
async def get_all_nodes_page(
    request: Request,
    nodes=Depends(get_all_nodes),
):
    return templates.TemplateResponse(
        "all_nodes.html", {"request": request, "nodes": nodes}
    )


@pages_router.get("/create_node")
async def get_create_node_page(request: Request):
    return templates.TemplateResponse("create_node.html", {"request": request})
