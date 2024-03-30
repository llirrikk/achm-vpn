#!/bin/bash

set -e

if [ "$#" -ne 7 ]; then
	echo "Usage: $0 <WG_CLIENT_CONFIG_PATH> <WG_CLIENT_ADDRESS> <WG_CLIENT_DNS> <WG_SERVER_ENDPOINT_HOST> <WG_SERVER_ENDPOINT_PORT> <WG_CLIENT_ALLOWED_IPS> <PERSISTENT_KEEPALIVE>"
	exit 1
fi
WG_CLIENT_CONFIG_PATH=$1  # /home/debian/client_wg.conf
WG_CLIENT_ADDRESS=$2  # 10.0.0.2/32
WG_CLIENT_DNS=$3  # 8.8.8.8
WG_SERVER_ENDPOINT_HOST=$4  # 192.168.1.122
WG_SERVER_ENDPOINT_PORT=$5  # 51830
WG_CLIENT_ALLOWED_IPS=$6  # 0.0.0.0/0
PERSISTENT_KEEPALIVE=$7  # 20

function isRoot() {
	if [ "${EUID}" -ne 0 ]; then
		echo "You need to run this script as root"
		exit 1
	fi
}
isRoot


client_private_key=$(sudo cat /etc/wireguard/client_privatekey)
server_pub_key=$(sudo cat /etc/wireguard/publickey)

sudo cat <<EOF >> "${WG_CLIENT_CONFIG_PATH}"
[Interface]
PrivateKey = ${client_private_key}
Address = ${WG_CLIENT_ADDRESS}
DNS = ${WG_CLIENT_DNS}

[Peer]
PublicKey = ${server_pub_key}
Endpoint = ${WG_SERVER_ENDPOINT_HOST}:${WG_SERVER_ENDPOINT_PORT}
AllowedIPs = ${WG_CLIENT_ALLOWED_IPS}
PersistentKeepalive = ${PERSISTENT_KEEPALIVE}
EOF

echo "Client configuration file created at ${WG_CLIENT_CONFIG_PATH}"
