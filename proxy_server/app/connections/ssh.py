import logging
from time import time
from typing import Self

import paramiko


logging.basicConfig()
logging.getLogger("paramiko").setLevel(logging.INFO)


class TimeExecution:
    def __enter__(self) -> Self:
        self.start = time()
        print("[TimeExecution] Start")
        return self

    def __exit__(self, *args):
        self.end = time()
        self.interval = self.end - self.start
        print(f"[TimeExecution] End. Elapsed time: {self.interval:.3f}s")


class SSHManager:
    def __init__(self, ssh_connection: paramiko.SSHClient):
        self.ssh = ssh_connection

    def send(self, command: str, timeout: int = 120) -> str:
        print(f"Sending command: {command}")
        stdin, stdout, stderr = self.ssh.exec_command(command, timeout=timeout)

        with TimeExecution():
            if stderr.read():
                print(f"Command: {command}")
                print(f"Exit code: {stdout.channel.recv_exit_status()}")
                print(f"Error: {stderr.read().decode()}")
                print(f"Output: {stdout.read().decode()}")
        return stdout.read().decode()

    def send_file(self, local_file: str, remote_file: str):
        print(f"Sending file {local_file} to {remote_file}")
        with self.ssh.open_sftp() as sftp:
            sftp.put(local_file, remote_file, confirm=False)


class SSHConnection:
    def __init__(
        self,
        host: str,
        port: int = 22,
        *,
        login: str,
        password: str,
        connection_timeout: int = 120,
    ):
        self.host = host
        self.port = port
        self.connection_timeout = connection_timeout
        self.login = login
        self.password = password

    def __enter__(self) -> SSHManager:
        print("[connect]")
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(
            self.host,
            port=self.port,
            timeout=self.connection_timeout,
            username=self.login,
            password=self.password,
        )
        return SSHManager(self.ssh)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("[disconnect]")
        self.ssh.close()


if __name__ == "__main__":
    with SSHConnection(
        "192.168.73.134",
        login="debian",
        password="debian",
    ) as ssh:
        result = ssh.send("ping 8.8.8.8 -c 2")
        print(result)
