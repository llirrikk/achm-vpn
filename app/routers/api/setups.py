from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.enums import VPNProtocolSchema
from app.manager import get_node_from_id, send_message_to_audit
from app.models.sql_database import get_db
from app.schemas import (
    SettingsCustomSchema,
    SettingsUnixWGClientSchema,
    SettingsUnixWGServerSchema,
)
from app.setups.custom_ssh import configure_custom_ssh
from app.setups.unix_wireguard_client import configure_wireguard_client
from app.setups.unix_wireguard_server import configure_wireguard_server

setups_router = APIRouter(
    prefix="/api/setups",
    tags=["api"],
)


@setups_router.post("/custom-setup")
async def setup_custom_setup(
    request: Request,
    settings_schema: SettingsCustomSchema,
    db_session: Session = Depends(get_db),
):
    node = get_node_from_id(db_session, settings_schema.node_id)
    print("Setting up custom setup...")
    send_message_to_audit(
        db_session,
        f"Произведена настройка кастомного сервера на узле {node.name}",
        request.client.host,
        request.client.port,
    )

    responses = await configure_custom_ssh(
        node, settings_schema.commands, proxy_address=settings_schema.proxy_address
    )
    node.add_network(
        db_session,
        name=settings_schema.network_name,
        node_role=settings_schema.role,
        vpn_protocol=settings_schema.protocol,
    )
    return {"status": "success", "responses": responses}


@setups_router.post("/unix-wireguard-server")
async def setup_unix_wg_server(
    request: Request,
    settings_schema: SettingsUnixWGServerSchema,
    db_session: Session = Depends(get_db),
):
    server = get_node_from_id(db_session, settings_schema.node_id)
    print("Setting up Wireguard server on UNIX...")
    send_message_to_audit(
        db_session,
        f"Произведена настройка Wireguard сервера на узле {server.name}",
        request.client.host,
        request.client.port,
    )

    configure_wireguard_server(server, settings_schema)

    server.add_network(
        db_session,
        name=settings_schema.network_name,
        node_role="SERVER",
        vpn_protocol=VPNProtocolSchema.WIREGUARD,
    )
    return {"status": "success"}


@setups_router.post("/unix-wireguard-client")
async def setup_unix_wg_client(
    request: Request,
    settings_schema: SettingsUnixWGClientSchema,
    db_session: Session = Depends(get_db),
) -> dict[str, str]:
    client = get_node_from_id(db_session, settings_schema.node_id)
    print("Setting up Wireguard server on UNIX...")
    send_message_to_audit(
        db_session,
        f"Произведена настройка Wireguard клиента на узле {client.name}",
        request.client.host,
        request.client.port,
    )

    configure_wireguard_client(client, settings_schema)

    client.add_network(
        db_session,
        name=settings_schema.network_name,
        node_role="CLIENT",
        vpn_protocol=VPNProtocolSchema.WIREGUARD,
    )
    return {"status": "success"}
