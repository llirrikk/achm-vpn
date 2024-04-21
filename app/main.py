import time
import uuid

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app.config import scheduler
from app.manager import send_message_to_audit
from app.models.base import AbstractBaseModel
from app.models.sql_database import SessionLocal, engine
from app.routers.api.events import events_router
from app.routers.api.monitoring_setups import monitoring_setups_router
from app.routers.api.nodes import node_router
from app.routers.api.nodes_connections import node_connections_router
from app.routers.api.proxy import proxy_router
from app.routers.api.scheduler import scheduler_router
from app.routers.api.setups import setups_router
from app.routers.pages.router import pages_router
from app.schemas import AppStatusSchema

AbstractBaseModel.metadata.create_all(bind=engine)


def start_scheduler():
    with SessionLocal() as db_session:
        send_message_to_audit(db_session, "Система запущена")
        scheduler.start()
        send_message_to_audit(db_session, "Планировщик задач запущен")
    print("scheduler inited")


def on_shutdown():
    with SessionLocal() as db_session:
        send_message_to_audit(db_session, "Система остановлена")
        scheduler.shutdown()
        send_message_to_audit(db_session, "Планировщик задач остановлен")
    print("scheduler shutdown")


app = FastAPI(
    title="VPN Setup and Monitoring",
    description="System for VPN Setup and Monitoring.",
    on_startup=[start_scheduler],
    on_shutdown=[scheduler.shutdown],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def add_response_uuid_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Response-UUID"] = str(uuid.uuid4())
    return response


@app.middleware("http")
async def record_audit(request: Request, call_next):
    with SessionLocal() as db_session:
        send_message_to_audit(
            db_session,
            f"Получен запрос {request.method} {request.url}",
            request.client.host,
            request.client.port,
        )
    response = await call_next(request)
    return response


app.mount("/misc", StaticFiles(directory="app/misc"), name="misc")


# API
app.include_router(node_router)
app.include_router(node_connections_router)
app.include_router(setups_router)
app.include_router(monitoring_setups_router)
app.include_router(scheduler_router)
app.include_router(events_router)
app.include_router(proxy_router)

# HTML
app.include_router(pages_router)


@app.get("/health", tags=["internal"])
async def health() -> AppStatusSchema:
    return AppStatusSchema(status="UP")
