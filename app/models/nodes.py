from typing import Literal

from pydantic import SecretStr
from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.enums import ConnectionProtocolSchema, SystemsSchema, VPNProtocolSchema
from app.models.base import AbstractBaseModel
from app.utils.fernet import encrypt


class Node(AbstractBaseModel):
    __tablename__ = "nodes"

    name = Column(String, nullable=False, index=True)
    system = Column(Enum(SystemsSchema), nullable=False)
    connections = relationship("Connection", back_populates="node")
    networks = relationship("Network", back_populates="node")

    def add_connection(self, connection: "Connection") -> "Connection":
        if len(self.connections) >= 2:
            raise ValueError(
                f"Node can have only two connections: SSH and TELNET. It already has {len(self.connections)} connections."
            )
        # Check if node already has connection with the same protocol
        for conn in self.connections:
            if conn.protocol.value == connection.protocol:
                raise ValueError(
                    f"Node already has connection with the same protocol: {connection.protocol}"
                )

        self.connections.append(connection)
        return connection

    def get_connection(self, protocol: ConnectionProtocolSchema) -> "Connection":
        for conn in self.connections:
            if conn.protocol == protocol:
                return conn
        raise ValueError(f"Node does not have connection with protocol: {protocol}")

    def add_network(
        self,
        db_session,
        *,
        name: str,
        node_role: Literal["SERVER", "CLIENT"],
        vpn_protocol: VPNProtocolSchema,
    ) -> "Network":
        existing_networks = len(self.networks)
        if existing_networks > 0:
            raise ValueError("Node already has network.")
        network = Network(
            name=name,
            protocol=vpn_protocol,
            node_id=self.id,
            node=self,
            node_role=node_role,
        )
        db_session.add(network)
        self.networks.append(network)
        db_session.commit()
        return network

    def get_network(self) -> "Network":
        if len(self.networks) == 0:
            raise ValueError("Node does not have any networks.")
        return self.networks[0]


class Connection(AbstractBaseModel):
    __tablename__ = "connections"

    protocol = Column(Enum(ConnectionProtocolSchema), nullable=False)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)  # Store encrypted password here

    node_id = Column(Integer, ForeignKey("nodes.id"))
    node = relationship("Node", back_populates="connections")

    def __init__(self, protocol, host, port, login, password, **kwargs):
        if isinstance(password, SecretStr):
            password = encrypt(password.get_secret_value())
        super().__init__(
            protocol=protocol,
            host=host,
            port=port,
            login=login,
            password=password,
            **kwargs,
        )


class Network(AbstractBaseModel):
    __tablename__ = "networks"

    name = Column(String, nullable=False)
    protocol = Column(Enum(VPNProtocolSchema), nullable=False)

    node_id = Column(Integer, ForeignKey("nodes.id"))
    node = relationship("Node", back_populates="networks")
    node_role = Column(String, nullable=False)
    grafana_url = Column(String, nullable=True)
