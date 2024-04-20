from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.manager import send_message_to_audit
from app.models.nodes import Connection, Node
from app.models.sql_database import get_db
from app.schemas import (
    ConnectionProtocolSchema,
    ConnectionSchema,
)
from app.utils.utils import parse_pydantic_schema

node_connections_router = APIRouter(
    prefix="/api/nodes/connections",
    tags=["api"],
)


@node_connections_router.post("/{node_id}/add")
async def create_connection(
    request: Request,
    node_id: int,
    connection_schema: ConnectionSchema,
    db_session: Session = Depends(get_db),
):
    # Create connection for node. Node can have only two connections: SSH and TELNET
    send_message_to_audit(
        db_session,
        f"Создано новое соединение для узла с id {node_id}",
        request.client.host,
        request.client.port,
    )
    node = db_session.query(Node).filter(Node.id == node_id).one_or_none()
    if not node:
        return JSONResponse({"status": "Node not found"}, status_code=404)

    connection = Connection(**parse_pydantic_schema(connection_schema))
    try:
        connection = node.add_connection(connection)
    except ValueError as e:
        return JSONResponse({"status": str(e)}, status_code=400)
    db_session.add(connection)
    db_session.commit()
    db_session.refresh(connection)
    return {"status": "ok", "connection_id": connection.id}


@node_connections_router.get("/{node_id}/<connection_type>")
async def get_connection(
    request: Request,
    node_id: int,
    connection_type: ConnectionProtocolSchema,
    db_session: Session = Depends(get_db),
):
    send_message_to_audit(
        db_session,
        f"Запрошено соединение {connection_type} для узла с id {node_id}",
        request.client.host,
        request.client.port,
    )
    node = db_session.query(Node).filter(Node.id == node_id).one_or_none()
    if not node:
        return JSONResponse({"status": "Node not found"}, status_code=404)

    try:
        connection = node.get_connection(connection_type)
    except ValueError as e:
        return JSONResponse({"status": str(e)}, status_code=400)

    return ConnectionSchema.model_validate(connection)
