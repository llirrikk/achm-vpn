from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, NonNegativeInt, SecretStr, validator

from app.enums import ConnectionProtocolSchema, SystemsSchema, VPNProtocolSchema
from app.models.nodes import Connection, Network, Node


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
    class NetworkShortSchema(BaseModel):
        name: str
        protocol: VPNProtocolSchema

        model_config = {"from_attributes": True}

        class Meta:
            orm_model = Network

    name: str
    system: SystemsSchema
    connections: list[ConnectionSchema]
    networks: list[NetworkShortSchema] = []

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


class NetworkSchema(BaseModel):
    name: str
    protocol: VPNProtocolSchema
    node: NodeSchemaWithID

    model_config = {"from_attributes": True}

    class Meta:
        orm_model = Network


class AggregatedNetworksSchema(BaseModel):
    id: NonNegativeInt
    name: str
    grafana_url: str | None
    protocol: VPNProtocolSchema
    server: list[NodeSchemaWithID]
    clients: list[NodeSchemaWithID]


class SchedulerSchema(BaseModel):
    node_id: NonNegativeInt
    command: str

    year: int | None = Field(None, ge=1000, le=9999, examples=[None, 1000])
    month: int | None = Field(None, ge=1, le=12, examples=[None, 1])
    day: int | None = Field(None, ge=1, le=31, examples=[None, 1])
    week: int | None = Field(None, ge=1, le=53, examples=[None, 1])
    day_of_week: Literal["sun", "mon", "tue", "wed", "thu", "fri", "sat"] | None = (
        Field(None, examples=[None, "mon"])
    )
    hour: int | None = Field(None, ge=0, le=23, examples=[None, 0])
    minute: int | None = Field(None, ge=0, le=59, examples=[None, 0])
    second: int | None | Literal["*"] = Field(None, examples=[None, "*"])
    start_date: datetime | str | None = Field(None, examples=[None])
    end_date: datetime | str | None = Field(None, examples=[None])


# Monitoring setup schemas


class MonitoringSetupSchema(BaseModel):
    network_id: NonNegativeInt
    node_id: NonNegativeInt
    commands: list[str]
    grafana_url: str


class EventSchema(BaseModel):
    id: NonNegativeInt
    created_at: datetime | str
    message: str

    @validator("created_at")
    def parse_created_at(cls, value):
        return datetime.strftime(value, "%d.%b.%Y %H:%M:%S")


# Node settings schemas


class SettingsSchemaBase(BaseModel):
    network_name: str
    node_id: int


class SettingsCustomSchema(SettingsSchemaBase):
    role: Literal["SERVER", "CLIENT"]
    commands: list[str]
    protocol: VPNProtocolSchema


class SettingsUnixWGServerSchema(SettingsSchemaBase):
    """
    {wg_address_mask}
    {wg_port}
    {wg_interface}
    {wg_client_allowed_ips}
    {wg_base_directory}

    {wg_client_config_path}
    {wg_client_address}
    {wg_client_dns}
    {wg_server_endpoint_host}
    {wg_server_endpoint_port}
    {wg_client_allowed_ips}
    {persistent_keepalive}
    """

    address_mask: str
    port: NonNegativeInt
    interface: str
    server_client_allowed_ips: str
    base_directory: str

    client_config_directory: str
    client_address_mask: str
    client_dns: str
    client_endpoint_host: str
    client_endpoint_port: NonNegativeInt
    client_allowed_ips: str
    client_persistent_keepalive: NonNegativeInt


class SettingsUnixWGClientSchema(SettingsSchemaBase):
    """
    {wg_client_private_key}
    {wg_client_address}
    {wg_client_dns_server}
    {wg_server_public_key}
    {wg_server_host}
    {wg_server_port}
    {wg_server_allowed_ips}
    {wg_server_persistent_keepalive}
    {wg_base_directory}
    """

    private_key: str
    address_mask: str
    dns_server: str
    server_public_key: str
    server_host: str
    server_port: NonNegativeInt
    server_allowed_ips: str
    server_persistent_keepalive: NonNegativeInt
    base_directory: str
