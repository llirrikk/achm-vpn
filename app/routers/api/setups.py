from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.manager import get_node_from_id
from app.models.sql_database import get_db
from app.schemas import SetupSchema
from app.setups.wireguard_server import configure_wireguard_server

setups_router = APIRouter(
    prefix="/api/setups",
    tags=["api"],
)


def setup_wg(setup_schema: SetupSchema, db_session: Session):
    if setup_schema.server_id is not None:
        server = get_node_from_id(db_session, setup_schema.server_id)

        print("Setting up Wireguard server...")
        configure_wireguard_server(server)


@setups_router.post("/")
async def setup_nodes(setup_schema: SetupSchema, db_session: Session = Depends(get_db)):
    match setup_schema.protocol:
        case "WIREGUARD":
            setup_wg(setup_schema, db_session)

        case "L2TP":
            pass

        case "PP2P":
            pass

        case _:
            return {"status": "error", "message": "Invalid protocol"}
