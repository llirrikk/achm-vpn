from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.manager import get_node_from_id
from app.models.sql_database import get_db
from app.schemas import SettingsUnixWGServerSchema
from app.setups.unix_wireguard_server import configure_wireguard_server

setups_router = APIRouter(
    prefix="/api/setups",
    tags=["api"],
)


@setups_router.post("/unix-wg-server")
async def setup_unix_wg_server(
    settings_schema: SettingsUnixWGServerSchema, db_session: Session = Depends(get_db)
):
    server = get_node_from_id(db_session, settings_schema.server_id)
    print("Setting up Wireguard server on UNIX...")
    configure_wireguard_server(server, settings_schema)

    return {"status": "success"}
