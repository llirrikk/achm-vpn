from app.models.nodes import Audit, Event, Network, Node, Proxy
from app.schemas import EventCreateSchema, ProxyCreateSchema


def get_node_from_id(db_session, node_id: int) -> Node:
    send_message_to_audit(db_session, f"Запрошен узел с id {node_id}")
    node = db_session.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise ValueError(f"Node with id {node_id} not found")
    return node


def get_network_from_id(db_session, network_id: int) -> Network:
    send_message_to_audit(db_session, f"Запрошена сеть с id {network_id}")
    network = db_session.query(Network).filter(Network.id == network_id).first()
    if not network:
        raise ValueError(f"Network with id {network_id} not found")
    return network


def set_grafana_url_to_network(db_session, network: Network, url: str) -> None:
    send_message_to_audit(
        db_session, f"Установлен URL Grafana {url} для сети {network.name}"
    )
    network.grafana_url = url  # type: ignore
    db_session.commit()
    print(f"Grafana URL set to {url} for network {network.name}")


def delete_grafa_url_from_network(db_session, network: Network) -> None:
    send_message_to_audit(db_session, f"Удален URL Grafana для сети {network.name}")
    network.grafana_url = None  # type: ignore
    db_session.commit()
    print(f"Grafana URL deleted from network {network.name}")


def get_all_events(db_session) -> list[Event]:
    send_message_to_audit(db_session, "Запрошены все события")
    return db_session.query(Event).all()


def create_event_db(db_session, event: EventCreateSchema) -> Event:
    new_event = Event(message=event.message)
    db_session.add(new_event)
    db_session.commit()
    send_message_to_audit(db_session, f"Полечено новое событие: {event.message}")
    return new_event


def get_all_audit(db_session) -> list[Audit]:
    return db_session.query(Audit).all()


def get_all_proxy(db_session) -> list[Proxy]:
    send_message_to_audit(db_session, "Запрошены все прокси")
    return db_session.query(Proxy).all()


def create_proxy_db(db_session, proxy: ProxyCreateSchema) -> None:
    new_proxy = Proxy(name=proxy.name, address=proxy.address)
    db_session.add(new_proxy)
    db_session.commit()
    send_message_to_audit(
        db_session, f"Создан новый прокси {proxy.name} с адресом {proxy.address}"
    )


def send_message_to_audit(
    db_session, message: str, ip: str | None = None, port: int | None = None
) -> None:
    audit = Audit(message=message, ip=f"{ip}:{port}")
    db_session.add(audit)
    db_session.commit()
