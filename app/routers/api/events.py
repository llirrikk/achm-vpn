from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.manager import get_all_events, create_event_db
from app.models.sql_database import get_db
from app.schemas import EventCreateSchema, EventSchema

events_router = APIRouter(
    prefix="/api/events",
    tags=["api"],
)


@events_router.get("/")
async def get_events(db_session: Session = Depends(get_db)) -> list[EventSchema]:
    return get_all_events(db_session)  # type: ignore


@events_router.post("/create")
async def create_event(
    event: EventCreateSchema, db_session: Session = Depends(get_db)
) -> EventSchema:
    return create_event_db(db_session, event)  # type: ignore
