import asyncio
import logging

from aio_pika import connect_robust
from aio_pika.abc import AbstractRobustConnection
from aio_pika.patterns import RPC

from app.config import settings
from message_models.models import MessageSchema


class RPCQueueClient:
    def __init__(self, rabbit_mq_url: str, timeout=10):
        self.timeout = timeout
        self.rabbit_mq_url = rabbit_mq_url
        self.connection: AbstractRobustConnection = None
        self.channel = None
        self.rpc: RPC = None

    async def __aenter__(self):
        self.connection = await connect_robust(
            self.rabbit_mq_url,
            client_properties={"connection_name": "caller"},
        )

        await self.connection.__aenter__()

        self.channel = await self.connection.channel()
        self.rpc = await RPC.create(self.channel)

        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.connection.__aexit__(exc_type, exc, tb)

    async def call(self, method_name: str, kwargs: dict):
        result = await asyncio.wait_for(
            self.rpc.call(method_name, kwargs=kwargs), timeout=self.timeout
        )
        return result


async def send_command(
    message: MessageSchema, rabbit_mq_url: str = settings.rabbit_mq_url
) -> str:
    async with RPCQueueClient(rabbit_mq_url, timeout=10) as rpc_client:
        logging.info("RPC call: %s", message)

        result = await rpc_client.call("send_command", kwargs=dict(message=message))
        return result
