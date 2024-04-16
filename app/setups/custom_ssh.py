from app.connections.ssh import SSHConnection
from app.enums import ConnectionProtocolSchema
from app.models.nodes import Connection, Node
from app.utils.fernet import decrypt


def configure_custom_ssh(
    node: Node, commands: list[str], ssh_connection: Connection | None = None
) -> list[str]:
    connection_to_be_used = None
    if ssh_connection is None:
        connection_to_be_used = node.get_connection(ConnectionProtocolSchema.SSH)
    else:
        connection_to_be_used = ssh_connection

    responses: list[str] = []

    with SSHConnection(
        connection_to_be_used.host,  # pyright: ignore[reportArgumentType]
        login=connection_to_be_used.login,  # pyright: ignore[reportArgumentType]
        password=decrypt(connection_to_be_used.password),  # pyright: ignore[reportArgumentType]
    ) as ssh:
        for command in commands:
            result = ssh.send(command)
            print(result)
            responses.append(result)
    return responses
