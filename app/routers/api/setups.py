from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.manager import get_node_from_id
from app.models.sql_database import get_db
from app.schemas import SettingsCustomSchema, SettingsUnixWGServerSchema
from app.setups.custom_ssh import configure_custom_ssh
from app.setups.unix_wireguard_server import configure_wireguard_server

setups_router = APIRouter(
    prefix="/api/setups",
    tags=["api"],
)


@setups_router.post("/custom-setup")
async def setup_custom_setup(
    settings_schema: SettingsCustomSchema, db_session: Session = Depends(get_db)
):
    node = get_node_from_id(db_session, settings_schema.server_id)
    print("Setting up custom setup...")
    responses = configure_custom_ssh(node, settings_schema)
    return {"status": "success", "responses": responses}


@setups_router.post("/unix-wireguard-server")
async def setup_unix_wg_server(
    settings_schema: SettingsUnixWGServerSchema, db_session: Session = Depends(get_db)
):
    server = get_node_from_id(db_session, settings_schema.server_id)
    print("Setting up Wireguard server on UNIX...")
    configure_wireguard_server(server, settings_schema)

    return {"status": "success"}
