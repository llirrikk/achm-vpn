import asyncio
import logging
from typing import NoReturn, assert_never

from aio_pika import connect_robust
from aio_pika.patterns import RPC

from app.config import RABBIT_MQ_URL
from app.connections.ssh import SSHConnection
from app.connections.telnet import TelnetConnection
from app.utils import temporary_file
from message_models.models import ConnectionProtocolSchema, MessageSchema

logger = logging.getLogger(__name__)
task_counter = 0


async def send_command(message: MessageSchema) -> str:
    global task_counter
    task_counter += 1
    logger.info("Получено сообщение: %s", message)

    match message.node_connection.protocol:
        case ConnectionProtocolSchema.SSH:
            with SSHConnection(
                host=message.node_connection.host,
                port=message.node_connection.port,
                login=message.node_connection.login,
                password=message.node_connection.password.get_secret_value(),
            ) as ssh:
                if message.file and message.file_name:
                    with temporary_file(message.file, filename=message.file_name):
                        ssh.send_file(message.file_name, f"/tmp/{message.file_name}")
                    return "Файл успешно отправлен"

                return ssh.send(message.command)
        case ConnectionProtocolSchema.TELNET:
            with TelnetConnection(
                host=message.node_connection.host, port=message.node_connection.port
            ) as telnet:
                telnet.login(
                    username=message.node_connection.login,
                    password=message.node_connection.password.get_secret_value(),
                )
                return str(telnet.send(message.command))
        case _:
            assert_never(message.node_connection.protocol)


async def start_app() -> NoReturn:
    global task_counter
    connection = await connect_robust(
        RABBIT_MQ_URL,
        client_properties={"connection_name": "callee"},
    )
    channel = await connection.channel()
    rpc = await RPC.create(channel)
    await channel.set_qos(prefetch_count=1)

    await rpc.register("send_command", send_command, durable=True)

    try:
        await asyncio.Future()
    except asyncio.exceptions.CancelledError:
        pass
    finally:
        await connection.close()
        logger.info("Было обработано %s задач", task_counter)


async def main() -> NoReturn:
    await start_app()
