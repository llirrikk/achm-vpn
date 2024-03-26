import enum


class SystemsSchema(enum.StrEnum):
    UNIX = "UNIX"
    CISCO = "CISCO"
    OPENWRT = "OPENWRT"
    MIKROTIK = "MIKROTIK"


class ConnectionProtocolSchema(enum.StrEnum):
    TELNET = "TELNET"
    SSH = "SSH"
