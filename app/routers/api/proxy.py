from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.manager import create_proxy_db, get_all_proxy
from app.models.sql_database import get_db
from app.schemas import ProxyCreateSchema, ProxySchema

proxy_router = APIRouter(
    prefix="/api/proxy",
    tags=["api"],
)


@proxy_router.get("/")
async def get_proxies(db_session: Session = Depends(get_db)) -> list[ProxySchema]:
    return get_all_proxy(db_session)  # type: ignore


@proxy_router.post("/create")
async def create_proxy(
    proxy_schema: ProxyCreateSchema,
    db_session: Session = Depends(get_db),
):
    create_proxy_db(db_session, proxy_schema)
