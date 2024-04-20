from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import TypeAdapter
from sqlalchemy.orm import Session

from app.manager import send_message_to_audit
from app.models.nodes import Network, Node
from app.models.sql_database import get_db
from app.schemas import (
    AggregatedNetworksSchema,
    NetworkSchema,
    NodeSchema,
    NodeSchemaWithID,
)
from app.utils.utils import parse_pydantic_schema

node_router = APIRouter(
    prefix="/api/nodes",
    tags=["api"],
)


@node_router.get("/")
async def get_all_nodes(
    request: Request,
    db_session: Session = Depends(get_db),
) -> list[NodeSchemaWithID]:
    send_message_to_audit(
        db_session,
        "Запрошены все узлы",
        request.client.host,
        request.client.port,
    )
    nodes = db_session.query(Node).all()
    type_adapter = TypeAdapter(list[NodeSchemaWithID])
    return type_adapter.validate_python(nodes)


@node_router.get("/{node_id}")
async def get_node(
    request: Request, node_id: int, db_session: Session = Depends(get_db)
):
    send_message_to_audit(
        db_session,
        f"Запрошен узел с id {node_id}",
        request.client.host,
        request.client.port,
    )
    node = db_session.query(Node).filter(Node.id == node_id).first()
    if not node:
        send_message_to_audit(
            db_session,
            f"Узел с id {node_id} не найден",
            request.client.host,
            request.client.port,
        )
        return JSONResponse({"status": "error", "message": "Node not found"}, 404)

    send_message_to_audit(
        db_session,
        f"Узел с id {node_id} найден",
        request.client.host,
        request.client.port,
    )
    type_adapter = TypeAdapter(NodeSchemaWithID)
    return type_adapter.validate_python(node)


@node_router.post("/create")
async def create_node(
    request: Request, node_schema: NodeSchema, db_session: Session = Depends(get_db)
):
    send_message_to_audit(
        db_session,
        f"Создан новый узел {node_schema.name}",
        request.client.host,
        request.client.port,
    )
    parsed_schema = parse_pydantic_schema(node_schema)
    node = Node(**parsed_schema)
    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)
    return {"status": "ok", "node_id": node.id}


@node_router.delete("/{node_id}")
async def delete_node(
    request: Request, node_id: int, db_session: Session = Depends(get_db)
):
    send_message_to_audit(
        db_session,
        f"Удален узел с id {node_id}",
        request.client.host,
        request.client.port,
    )
    node = db_session.query(Node).filter(Node.id == node_id).first()
    if not node:
        return JSONResponse({"status": "error", "message": "Node not found"}, 404)
    db_session.delete(node)
    db_session.commit()
    return {"status": "ok"}


@node_router.get("/networks/")
async def get_all_networks(
    request: Request,
    db_session: Session = Depends(get_db),
) -> list[AggregatedNetworksSchema]:
    send_message_to_audit(
        db_session,
        "Запрошены все сети",
        request.client.host,
        request.client.port,
    )
    networks = db_session.query(Network).all()
    unique_networks: dict[
        str, tuple[list[NodeSchemaWithID], list[NodeSchemaWithID], str, int, str | None]
    ] = {}
    for network in networks:
        unique_networks.setdefault(
            network.name,  # pyright: ignore[reportArgumentType]
            (
                [],
                [],
                network.protocol,
                network.id,
                network.grafana_url,
            ),  # pyright: ignore[reportArgumentType]
        )
        if network.node_role == "SERVER":  # pyright: ignore[reportGeneralTypeIssues]
            unique_networks[network.name][0].append(
                network.node
            )  # pyright: ignore[reportArgumentType]
        else:
            unique_networks[network.name][1].append(
                network.node
            )  # pyright: ignore[reportArgumentType]

    unique_networks_to_serialize = []
    for network_name, nodes in unique_networks.items():
        server, clients, network_protocol, network_id, grafana_url = nodes
        unique_networks_to_serialize.append(
            {
                "id": network_id,
                "name": network_name,
                "grafana_url": grafana_url,
                "protocol": network_protocol,
                "server": server,
                "clients": clients,
            }
        )

    type_adapter = TypeAdapter(list[AggregatedNetworksSchema])
    return type_adapter.validate_python(unique_networks_to_serialize)


@node_router.get("/networks/{node_id}")
async def get_node_networks(
    request: Request, node_id: int, db_session: Session = Depends(get_db)
):
    send_message_to_audit(
        db_session,
        f"Запрошены сети для узла с id {node_id}",
        request.client.host,
        request.client.port,
    )
    node = db_session.query(Node).filter(Node.id == node_id).first()
    if not node:
        return JSONResponse({"status": "error", "message": "Node not found"}, 404)
    if not node.networks:
        return JSONResponse(
            {"status": "error", "message": "Node does not have any networks"}, 404
        )
    type_adapter = TypeAdapter(NetworkSchema)
    return type_adapter.validate_python(node.get_network())
