import enum

from pydantic import BaseModel, SecretStr, field_validator


class ConnectionProtocolSchema(enum.StrEnum):
    TELNET = "TELNET"
    SSH = "SSH"


class NodeConnectionSchema(BaseModel):
    protocol: ConnectionProtocolSchema
    host: str
    port: int
    login: str
    password: SecretStr


class MessageSchema(BaseModel):
    node_connection: NodeConnectionSchema
    command: str
    file: bytes | None = None
    file_name: str | None = None

    @field_validator("file")
    def validate_file(cls, value: bytes, values) -> bytes:
        """validate that file only if node_connection is SSH"""
        if (
            values.data["node_connection"].protocol == ConnectionProtocolSchema.TELNET
            and value is not None
        ):
            raise ValueError("File can only be sent over SSH protocol")
        return value

    @field_validator("file_name")
    def validate_file_name(cls, value: str, values) -> str:
        """validate that file_name only with file"""
        if values.data["file"] is None and value is not None:
            raise ValueError("File name can only be set with file")
        if values.data["file"] is not None and value is None:
            raise ValueError("File name must be set with file")
        return value
