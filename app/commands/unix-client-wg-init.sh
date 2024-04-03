#!/bin/bash

set -e

if [ "$#" -ne 9 ]; then
	echo "Usage: $0 <WG_CLIENT_PRIVATE_KEY> <WG_CLIENT_ADDRESS> <WG_CLIENT_DNS_SERVER> <WG_SERVER_PUBLIC_KEY> <WG_SERVER_HOST> <WG_SERVER_PORT> <WG_SERVER_ALLOWED_IPS> <WG_SERVER_PERSISTENT_KEEPALIVE> <WG_BASE_DIRECTORY>"
	exit 1
fi

WG_CLIENT_PRIVATE_KEY=$1  # sK9J8dNGM9WpkqMk/quKvfw/AgOT9CXExIKIlba1CmI=
WG_CLIENT_ADDRESS=$2  # 10.0.0.2/32
WG_CLIENT_DNS_SERVER=$3  # 8.8.8.8
WG_SERVER_PUBLIC_KEY=$4  # Mr+LrABHypveJFsoR5gkcoPEBnloOqbbg5LTzfui2Bc=
WG_SERVER_HOST=$5  # 192.168.1.122
WG_SERVER_PORT=$6  # 51830
WG_SERVER_ALLOWED_IPS=$7  # 0.0.0.0/0
WG_SERVER_PERSISTENT_KEEPALIVE=$8  # 20
WG_BASE_DIRECTORY=$9  # /home/debian


function isRoot() {
	if [ "${EUID}" -ne 0 ]; then
		echo "You need to run this script as root"
		exit 1
	fi
}
isRoot

# sudo apt update && sudo apt upgrade -y
# sudo apt install -y wireguard
# sudo apt install resolvconf iptables -y


sudo cat <<EOF > "${WG_BASE_DIRECTORY}/wg0.conf"
[Interface]
PrivateKey = ${WG_CLIENT_PRIVATE_KEY}
Address = ${WG_CLIENT_ADDRESS}
DNS = ${WG_CLIENT_DNS_SERVER}

[Peer]
PublicKey = ${WG_SERVER_PUBLIC_KEY}
Endpoint = ${WG_SERVER_HOST}:${WG_SERVER_PORT}
AllowedIPs = ${WG_SERVER_ALLOWED_IPS}
PersistentKeepalive = ${WG_SERVER_PERSISTENT_KEEPALIVE}

EOF

sudo mv ${WG_BASE_DIRECTORY}/wg0.conf /etc/wireguard/wg0.conf

sudo wg-quick down wg0
sudo wg-quick up wg0
sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0

echo "Client configuration is done."
