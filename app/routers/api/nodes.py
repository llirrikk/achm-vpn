from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import TypeAdapter
from sqlalchemy.orm import Session

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


@node_router.get("/get_all")
async def get_all_nodes(
    db_session: Session = Depends(get_db),
) -> list[NodeSchemaWithID]:
    nodes = db_session.query(Node).all()
    type_adapter = TypeAdapter(list[NodeSchemaWithID])
    return type_adapter.validate_python(nodes)


@node_router.get("/get/{node_id}")
async def get_node(node_id: int, db_session: Session = Depends(get_db)):
    node = db_session.query(Node).filter(Node.id == node_id).first()
    if not node:
        return JSONResponse({"status": "error", "message": "Node not found"}, 404)
    type_adapter = TypeAdapter(NodeSchemaWithID)
    return type_adapter.validate_python(node)


@node_router.post("/create")
async def create_node(node_schema: NodeSchema, db_session: Session = Depends(get_db)):
    parsed_schema = parse_pydantic_schema(node_schema)
    node = Node(**parsed_schema)
    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)
    return {"status": "ok", "node_id": node.id}


@node_router.delete("/delete/{node_id}")
async def delete_node(node_id: int, db_session: Session = Depends(get_db)):
    node = db_session.query(Node).filter(Node.id == node_id).first()
    if not node:
        return JSONResponse({"status": "error", "message": "Node not found"}, 404)
    db_session.delete(node)
    db_session.commit()
    return {"status": "ok"}


@node_router.get("/networks/")
async def get_all_networks(
    db_session: Session = Depends(get_db),
) -> list[AggregatedNetworksSchema]:
    networks = db_session.query(Network).all()
    unique_networks: dict[
        str, tuple[list[NodeSchemaWithID], list[NodeSchemaWithID], str, int]
    ] = {}
    for network in networks:
        unique_networks.setdefault(network.name, ([], [], network.protocol, network.id))  # pyright: ignore[reportArgumentType]
        if network.node_role == "SERVER":  # pyright: ignore[reportGeneralTypeIssues]
            unique_networks[network.name][0].append(network.node)  # pyright: ignore[reportArgumentType]
        else:
            unique_networks[network.name][1].append(network.node)  # pyright: ignore[reportArgumentType]

    unique_networks_to_serialize = []
    for network_name, nodes in unique_networks.items():
        server, clients, network_protocol, network_id = nodes
        unique_networks_to_serialize.append(
            {
                "id": network_id,
                "name": network_name,
                "protocol": network_protocol,
                "server": server,
                "clients": clients,
            }
        )

    type_adapter = TypeAdapter(list[AggregatedNetworksSchema])
    return type_adapter.validate_python(unique_networks_to_serialize)


@node_router.get("/networks/{node_id}")
async def get_node_networks(node_id: int, db_session: Session = Depends(get_db)):
    node = db_session.query(Node).filter(Node.id == node_id).first()
    if not node:
        return JSONResponse({"status": "error", "message": "Node not found"}, 404)
    if not node.networks:
        return JSONResponse(
            {"status": "error", "message": "Node does not have any networks"}, 404
        )
    type_adapter = TypeAdapter(NetworkSchema)
    return type_adapter.validate_python(node.get_network())
