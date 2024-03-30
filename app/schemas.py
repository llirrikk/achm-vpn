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


class NodeSchemaWithID(NodeSchema):
    id: int


class ProtocolSchema(enum.StrEnum):
    WIREGUARD = "WIREGUARD"
    L2TP = "L2TP"
    OPENVPN = "OPENVPN"


class SetupSchema(BaseModel):
    server: NodeSchema | None = None
    clients: list[NodeSchema] = []
    protocol: ProtocolSchema
