from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import scheduler
from app.enums import ConnectionProtocolSchema
from app.manager import get_node_from_id
from app.models.nodes import Connection, Node
from app.models.sql_database import get_db
from app.schemas import SchedulerSchema
from app.setups.custom_ssh import configure_custom_ssh


def execute_command(node: Node, command: str, ssh_connection: Connection):
    configure_custom_ssh(node, [command], ssh_connection)


def schedule_job(
    scheduler_schema: SchedulerSchema,
    node: Node,
    command: str,
    ssh_connection: Connection,
) -> None:
    scheduler.add_job(
        execute_command,
        "cron",
        year=scheduler_schema.year,
        month=scheduler_schema.month,
        day=scheduler_schema.day,
        week=scheduler_schema.week,
        day_of_week=scheduler_schema.day_of_week,
        hour=scheduler_schema.hour,
        minute=scheduler_schema.minute,
        second=scheduler_schema.second,
        start_date=scheduler_schema.start_date,
        end_date=scheduler_schema.end_date,
        args=[node, command, ssh_connection],
    )


scheduler_router = APIRouter(
    prefix="/api/scheduler",
    tags=["api"],
)


@scheduler_router.post("/")
async def setup_custom_setup(
    scheduler_schema: SchedulerSchema, db_session: Session = Depends(get_db)
) -> dict[str, str]:
    node = get_node_from_id(db_session, scheduler_schema.node_id)
    print(f"Setting up scheduler for {node=}")
    schedule_job(
        scheduler_schema,
        node,
        scheduler_schema.command,
        node.get_connection(ConnectionProtocolSchema.SSH),
    )

    return {"status": "success"}
