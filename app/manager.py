from app.models.nodes import Event, Network, Node


def get_node_from_id(db_session, node_id: int) -> Node:
    node = db_session.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise ValueError(f"Node with id {node_id} not found")
    return node


def get_network_from_id(db_session, network_id: int) -> Network:
    network = db_session.query(Network).filter(Network.id == network_id).first()
    if not network:
        raise ValueError(f"Network with id {network_id} not found")
    return network


def set_grafana_url_to_network(db_session, network: Network, url: str) -> None:
    network.grafana_url = url  # type: ignore
    db_session.commit()
    print(f"Grafana URL set to {url} for network {network.name}")


def delete_grafa_url_from_network(db_session, network: Network) -> None:
    network.grafana_url = None  # type: ignore
    db_session.commit()
    print(f"Grafana URL deleted from network {network.name}")


def get_all_events(db_session) -> list[Event]:
    return db_session.query(Event).all()
