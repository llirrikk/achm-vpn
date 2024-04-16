from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.manager import get_all_events
from app.models.sql_database import get_db
from app.schemas import EventSchema

events_router = APIRouter(
    prefix="/api/events",
    tags=["api"],
)


@events_router.get("/")
async def get_events(db_session: Session = Depends(get_db)) -> list[EventSchema]:
    return get_all_events(db_session)  # type: ignore
