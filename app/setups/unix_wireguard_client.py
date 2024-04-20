from app.connections.ssh import SSHConnection
from app.enums import ConnectionProtocolSchema
from app.models.nodes import Node
from app.schemas import SettingsUnixWGClientSchema
from app.utils.fernet import decrypt

unix_wg_client_init = "sudo /dev/shm/unix-wg-client-init.sh {wg_client_private_key} {wg_client_address} {wg_client_dns_server} {wg_server_public_key} {wg_server_host} {wg_server_port} {wg_server_allowed_ips} {wg_server_persistent_keepalive} {wg_base_directory}"


def configure_wireguard_client(
    client: Node, settings_schema: SettingsUnixWGClientSchema
):
    ssh_connection = client.get_connection(ConnectionProtocolSchema.SSH)

    with SSHConnection(
        ssh_connection.host,  # pyright: ignore[reportArgumentType]
        login=ssh_connection.login,  # pyright: ignore[reportArgumentType]
        password=decrypt(
            ssh_connection.password
        ),  # pyright: ignore[reportArgumentType]
    ) as ssh:
        ssh.send_file(
            "app/commands/unix-wg-client-init.sh",
            "/dev/shm/unix-wg-client-init.sh",
        )
        ssh.send("sudo chmod +x /dev/shm/unix-wg-client-init.sh")

        print("unix_wg_client_init: start")
        result = ssh.send(
            unix_wg_client_init.format(
                wg_client_private_key=settings_schema.private_key,
                wg_client_address=settings_schema.address_mask,
                wg_client_dns_server=settings_schema.dns_server,
                wg_server_public_key=settings_schema.server_public_key,
                wg_server_host=settings_schema.server_host,
                wg_server_port=settings_schema.server_port,
                wg_server_allowed_ips=settings_schema.server_allowed_ips,
                wg_server_persistent_keepalive=settings_schema.server_persistent_keepalive,
                wg_base_directory=settings_schema.base_directory,
            )
        )
        print(result)
