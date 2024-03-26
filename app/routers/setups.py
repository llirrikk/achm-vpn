from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.models.sql_database import get_db
from app.schemas import SetupSchema

setups_router = APIRouter(
    prefix="/setups",
)


@setups_router.post("/")
async def setup_nodes(setup_schema: SetupSchema, db_session: Session = Depends(get_db)):
    print(setup_schema)

    return {"status": "ok"}
