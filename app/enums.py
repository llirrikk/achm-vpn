import enum


class SystemsSchema(enum.StrEnum):
    UNIX = "UNIX"
    CISCO = "CISCO"
    OPENWRT = "OPENWRT"
    MIKROTIK = "MIKROTIK"


class ConnectionProtocolSchema(enum.StrEnum):
    TELNET = "TELNET"
    SSH = "SSH"


class VPNProtocolSchema(enum.StrEnum):
    WIREGUARD = "WIREGUARD"
    L2TP = "L2TP"
    PP2P = "PP2P"
