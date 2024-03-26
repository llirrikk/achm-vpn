from fastapi import APIRouter, Depends
from pydantic import TypeAdapter
from sqlalchemy.orm import Session

from app.models.nodes import Node
from app.models.sql_database import get_db
from app.schemas import NodeSchema
from app.utils.utils import parse_pydantic_schema

node_router = APIRouter(
    prefix="/nodes",
)


@node_router.get("/get_all")
async def get_all_nodes(db_session: Session = Depends(get_db)) -> list[NodeSchema]:
    nodes = db_session.query(Node).all()
    type_adapter = TypeAdapter(list[NodeSchema])
    return type_adapter.validate_python(nodes)


@node_router.post("/create")
async def create_node(node_schema: NodeSchema, db_session: Session = Depends(get_db)):
    parsed_schema = parse_pydantic_schema(node_schema)
    node = Node(**parsed_schema)
    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)
    return {"status": "ok", "node_id": node.id}
