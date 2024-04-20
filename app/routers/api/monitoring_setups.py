from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.manager import (
    delete_grafa_url_from_network,
    get_network_from_id,
    get_node_from_id,
    send_message_to_audit,
    set_grafana_url_to_network,
)
from app.models.sql_database import get_db
from app.schemas import (
    MonitoringSetupSchema,
)
from app.setups.custom_monitoring import configure_custom_monitoring_ssh

monitoring_setups_router = APIRouter(
    prefix="/api/monitoring-setups",
    tags=["api"],
)


@monitoring_setups_router.post("/")
async def setup_custom_monitoring_setup(
    request: Request,
    settings_schema: MonitoringSetupSchema,
    db_session: Session = Depends(get_db),
):
    send_message_to_audit(
        db_session,
        f"Производится настройка мониторинга {settings_schema}",
        request.client.host,
        request.client.port,
    )
    node = get_node_from_id(db_session, settings_schema.node_id)
    network = get_network_from_id(db_session, settings_schema.network_id)
    print("Setting up monitoring...")
    responses = configure_custom_monitoring_ssh(node, settings_schema)
    set_grafana_url_to_network(db_session, network, settings_schema.grafana_url)

    return {"status": "success", "responses": responses}


@monitoring_setups_router.delete("/{network_id}")
async def delete_monitoring_setup(
    request: Request, network_id: int, db_session: Session = Depends(get_db)
):
    send_message_to_audit(
        db_session,
        f"Удаление настройки мониторинга сети {network_id}",
        request.client.host,
        request.client.port,
    )
    network = get_network_from_id(db_session, network_id)
    print("Deleting monitoring setup...")
    delete_grafa_url_from_network(db_session, network)
    return {"status": "success"}
