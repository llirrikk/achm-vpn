import enum
from typing import Literal

from pydantic import BaseModel, SecretStr, validator

from app.enums import ConnectionProtocolSchema, SystemsSchema
from app.models.nodes import Connection, Node


class AppStatusSchema(BaseModel):
    status: Literal["UP"]


class ConnectionSchema(BaseModel):
    protocol: ConnectionProtocolSchema
    host: str
    port: int
    login: str
    password: SecretStr

    model_config = {"from_attributes": True}

    class Meta:
        orm_model = Connection

    @validator("password", pre=True)
    def parse_bytes_to_secret_str(cls, value) -> SecretStr:
        if isinstance(value, bytes):
            return SecretStr(value.decode())
        return value


class NodeSchema(BaseModel):
    name: str
    system: SystemsSchema
    connections: list[ConnectionSchema]

    model_config = {"from_attributes": True}

    class Meta:
        orm_model = Node

    def get_ssh_connection(self) -> ConnectionSchema | None:
        for connection in self.connections:
            if connection.protocol == ConnectionProtocolSchema.SSH:
                return connection
        return None

    def get_telnet_connection(self) -> ConnectionSchema | None:
        for connection in self.connections:
            if connection.protocol == ConnectionProtocolSchema.TELNET:
                return connection
        return None


class NodeSchemaWithID(NodeSchema):
    id: int


class ProtocolSchema(enum.StrEnum):
    WIREGUARD = "WIREGUARD"
    L2TP = "L2TP"
    PP2P = "PP2P"


class SetupSchema(BaseModel):
    server_id: int | None = None
    clients_id: list[int] = []
    protocol: ProtocolSchema
