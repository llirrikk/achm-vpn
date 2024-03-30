from app.connections.ssh import SSHConnection
from app.enums import ConnectionProtocolSchema
from app.models.nodes import Node
from app.utils.fernet import decrypt


def configure_wireguard_server(server: Node):
    ssh_connection = server.get_connection(ConnectionProtocolSchema.SSH)

    with SSHConnection(
        ssh_connection.host,  # type: ignore
        login=ssh_connection.login,  # type: ignore
        password=decrypt(ssh_connection.password),  # type: ignore
    ) as ssh:
        # result = ssh.send("ping 8.8.8.8 -c 2")
        # print(result)
        ssh.send_file(
            "app/commands/unix-server-wg-init.sh", "/home/debian/unix-server-wg-init.sh"
        )
        ssh.send("chmod +x /home/debian/unix-server-wg-init.sh")
        result = ssh.send(
            "sudo /home/debian/unix-server-wg-init.sh 10.0.0.1/24 51830 ens4 10.0.0.2/32 /etc/wireguard"
        )
        print(result)
