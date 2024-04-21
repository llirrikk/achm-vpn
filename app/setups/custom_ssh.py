from app.connections.ssh import SSHConnection
from app.enums import ConnectionProtocolSchema
from app.models.nodes import Connection, Node
from app.queue.rpc import send_command
from app.utils.fernet import decrypt
from message_models.models import MessageSchema as RPCMessageSchema
from message_models.models import NodeConnectionSchema as RPCNodeConnectionSchema
from message_models.models import (
    ConnectionProtocolSchema as RPCConnectionProtocolSchema,
)


async def configure_custom_ssh(
    node: Node,
    commands: list[str],
    ssh_connection: Connection | None = None,
    proxy_address: str | None = None,
) -> list[str]:
    connection_to_be_used = None
    if ssh_connection is None:
        connection_to_be_used = node.get_connection(ConnectionProtocolSchema.SSH)
    else:
        connection_to_be_used = ssh_connection

    responses: list[str] = []

    if proxy_address:
        for command in commands:
            message = RPCMessageSchema(
                node_connection=RPCNodeConnectionSchema(
                    protocol=RPCConnectionProtocolSchema.SSH,
                    host=connection_to_be_used.host,  # pyright: ignore[reportArgumentType]
                    port=22,
                    login=connection_to_be_used.login,  # pyright: ignore[reportArgumentType]
                    password=decrypt(
                        connection_to_be_used.password  # pyright: ignore[reportArgumentType]
                    ),
                ),
                command=command,
            )
            result = await send_command(message, rabbit_mq_url=proxy_address)
            responses.append(result)
        return responses

    with SSHConnection(
        connection_to_be_used.host,  # pyright: ignore[reportArgumentType]
        login=connection_to_be_used.login,  # pyright: ignore[reportArgumentType]
        password=decrypt(
            connection_to_be_used.password  # pyright: ignore[reportArgumentType]
        ),
    ) as ssh:
        for command in commands:
            result = ssh.send(command)
            print(result)
            responses.append(result)
    return responses
