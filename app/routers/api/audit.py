from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.manager import get_all_audit
from app.models.sql_database import get_db
from app.schemas import AuditSchema

audit_router = APIRouter(
    prefix="/api/audit",
    tags=["api"],
)


@audit_router.get("/")
async def get_audit(db_session: Session = Depends(get_db)) -> list[AuditSchema]:
    return get_all_audit(db_session)  # type: ignore
