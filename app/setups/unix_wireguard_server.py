from app.connections.ssh import SSHConnection
from app.enums import ConnectionProtocolSchema
from app.models.nodes import Node
from app.schemas import SettingsUnixWGServerSchema
from app.utils.fernet import decrypt

unix_wg_server_init = "sudo /dev/shm/unix-wg-server-init.sh {wg_address_mask} {wg_port} {wg_interface} {wg_client_allowed_ips} {wg_base_directory}"
unix_wg_server_create_client_config = "sudo /dev/shm/unix-wg-server-create-client-config.sh {wg_client_config_path} {wg_client_address} {wg_client_dns} {wg_server_endpoint_host} {wg_server_endpoint_port} {wg_client_allowed_ips} {persistent_keepalive}"


def configure_wireguard_server(
    server: Node, settings_schema: SettingsUnixWGServerSchema
):
    ssh_connection = server.get_connection(ConnectionProtocolSchema.SSH)

    with SSHConnection(
        ssh_connection.host,  # pyright: ignore[reportArgumentType]
        login=ssh_connection.login,  # pyright: ignore[reportArgumentType]
        password=decrypt(
            ssh_connection.password
        ),  # pyright: ignore[reportArgumentType]
    ) as ssh:
        # first file
        ssh.send_file(
            "app/commands/unix-wg-server-init.sh",
            "/dev/shm/unix-wg-server-init.sh",
        )
        ssh.send("sudo chmod +x /dev/shm/unix-wg-server-init.sh")

        # second file
        ssh.send_file(
            "app/commands/unix-wg-server-create-client-config.sh",
            "/dev/shm/unix-wg-server-create-client-config.sh",
        )
        ssh.send("sudo chmod +x /dev/shm/unix-wg-server-create-client-config.sh")

        print("unix_wg_server_init: start")
        result = ssh.send(
            unix_wg_server_init.format(
                wg_address_mask=settings_schema.address_mask,
                wg_port=settings_schema.port,
                wg_interface=settings_schema.interface,
                wg_client_allowed_ips=settings_schema.server_client_allowed_ips,
                wg_base_directory=settings_schema.base_directory,
            )
        )
        print(result)

        print("unix_wg_server_create_client_config: start")
        result = ssh.send(
            unix_wg_server_create_client_config.format(
                wg_client_config_path=settings_schema.client_config_directory,
                wg_client_address=settings_schema.client_address_mask,
                wg_client_dns=settings_schema.client_dns,
                wg_server_endpoint_host=settings_schema.client_endpoint_host,
                wg_server_endpoint_port=settings_schema.client_endpoint_port,
                wg_client_allowed_ips=settings_schema.client_allowed_ips,
                persistent_keepalive=settings_schema.client_persistent_keepalive,
            )
        )
        print(result)
