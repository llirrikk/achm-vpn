from app.models.nodes import Node


def get_node_from_id(db_session, node_id: int) -> Node:
    node = db_session.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise ValueError(f"Node with id {node_id} not found")
    return node
