from app.connections.ssh import SSHConnection
from app.enums import ConnectionProtocolSchema
from app.models.nodes import Node
from app.schemas import SettingsCustomSchema
from app.utils.fernet import decrypt


def configure_custom_ssh(
    node: Node, settings_schema: SettingsCustomSchema
) -> list[str]:
    ssh_connection = node.get_connection(ConnectionProtocolSchema.SSH)

    responses: list[str] = []

    with SSHConnection(
        ssh_connection.host,  # pyright: ignore[reportArgumentType]
        login=ssh_connection.login,  # pyright: ignore[reportArgumentType]
        password=decrypt(ssh_connection.password),  # pyright: ignore[reportArgumentType]
    ) as ssh:
        for command in settings_schema.commands:
            result = ssh.send(command)
            print(result)
            responses.append(result)
    return responses
