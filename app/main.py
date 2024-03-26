from fastapi import FastAPI

from app.models.base import AbstractBaseModel
from app.models.sql_database import engine
from app.routers.nodes import node_router
from app.routers.nodes_connections import node_connections_router
from app.routers.setups import setups_router
from app.schemas import AppStatusSchema

AbstractBaseModel.metadata.create_all(bind=engine)

app = FastAPI(
    title="VPN Setup and Monitoring",
    description="System for VPN Setup and Monitoring.",
)

app.include_router(node_router)
app.include_router(node_connections_router)
app.include_router(setups_router)


@app.get("/health", tags=["internal"])
async def health() -> AppStatusSchema:
    return AppStatusSchema(status="UP")
