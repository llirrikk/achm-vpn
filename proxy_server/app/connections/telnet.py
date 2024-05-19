import telnetlib
import time
from typing import Sequence

LINE_ENDING = b"\n"


class TelnetManager:
    def __init__(self, telnet_connection: telnetlib.Telnet):
        self.telnet = telnet_connection

    @staticmethod
    def _str_to_bytes(string: str) -> bytes:
        return string.encode()

    def _await_prompts(self, prompts: Sequence[str]):
        index, match, out = self.telnet.expect(
            list(map(self._str_to_bytes, prompts)), timeout=10
        )
        if not match:
            raise TimeoutError(prompts)
        return out

    def send(
        self,
        text: str,
        *,
        await_before: Sequence[str] | None = None,
        await_after: Sequence[str] | None = None,
    ) -> bytes | None:
        if await_after is None:
            await_after = ["\\$"]

        if await_before is not None:
            self._await_prompts(await_before)

        self.telnet.write(self._str_to_bytes(text) + LINE_ENDING)

        if await_after is None:
            return None
        time.sleep(1)
        response = self._await_prompts(await_after)
        return response

    def login(self, username: str, password: str) -> None:
        self.send("", await_before=None, await_after="debian login:")
        self.send(username, await_before="debian login:", await_after="Password:")
        self.send(password, await_before="Password:", await_after=None)


class TelnetConnection:
    def __init__(self, host: str, port: int, *, connection_timeout: int = 120):
        self.host = host
        self.port = port
        self.connection_timeout = connection_timeout

    def __enter__(self) -> TelnetManager:
        print("[connect]")
        self.telnet = telnetlib.Telnet(self.host, self.port, self.connection_timeout)
        return TelnetManager(self.telnet)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("[disconnect]")
        self.telnet.write(b"exit" + LINE_ENDING)
        self.telnet.expect([b"logout"], timeout=3)
        self.telnet.close()


if __name__ == "__main__":
    with TelnetConnection("192.168.73.128", 5018) as telnet:
        telnet.login("debian", "debian")

        telnet.send("sudo dhclient ens4")
        result = telnet.send("ping 8.8.8.8 -c 3")
        print(result)
