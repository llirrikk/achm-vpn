from fastapi import FastAPI

from app.config import scheduler
from app.models.base import AbstractBaseModel
from app.models.sql_database import engine
from app.routers.api.events import events_router
from app.routers.api.monitoring_setups import monitoring_setups_router
from app.routers.api.nodes import node_router
from app.routers.api.nodes_connections import node_connections_router
from app.routers.api.scheduler import scheduler_router
from app.routers.api.setups import setups_router
from app.routers.pages.router import pages_router
from app.schemas import AppStatusSchema

AbstractBaseModel.metadata.create_all(bind=engine)


def start_scheduler():
    scheduler.start()
    print("scheduler inited")


app = FastAPI(
    title="VPN Setup and Monitoring",
    description="System for VPN Setup and Monitoring.",
    on_startup=[start_scheduler],
)


# API
app.include_router(node_router)
app.include_router(node_connections_router)
app.include_router(setups_router)
app.include_router(monitoring_setups_router)
app.include_router(scheduler_router)
app.include_router(events_router)

# HTML
app.include_router(pages_router)


@app.get("/health", tags=["internal"])
async def health() -> AppStatusSchema:
    return AppStatusSchema(status="UP")
