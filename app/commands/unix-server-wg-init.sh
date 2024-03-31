#!/bin/bash

set -e

if [ "$#" -ne 5 ]; then
	echo "Usage: $0 <WG_ADDRESS_MASK> <WG_PORT> <WG_INTERFACE> <WG_CLIENT_ALLOWED_IPS> <WG_BASE_DIRECTORY>"
	exit 1
fi
WG_ADDRESS_MASK=$1  # 10.0.0.1/24
WG_PORT=$2  # 51830
WG_INTERFACE=$3  # ens4
WG_CLIENT_ALLOWED_IPS=$4  # 10.0.0.2/32
WG_BASE_DIRECTORY=$5  # /etc/wireguard

function isRoot() {
	if [ "${EUID}" -ne 0 ]; then
		echo "You need to run this script as root"
		exit 1
	fi
}
isRoot

function appendLineToFileIfNotExists() {
	if [ "$#" -ne 2 ]; then
		echo "Usage: appendLineToFileIfNotExists <file> <line>"
		exit 1
	fi
	local file=$1
	local line=$2
	grep -qF -- "${line}" "${file}" || echo "${line}" >> "${file}"
}

# sudo apt update && sudo apt upgrade -y
# sudo apt install -y wireguard

sudo wg genkey | sudo tee "${WG_BASE_DIRECTORY}/privatekey" | sudo wg pubkey | sudo tee "${WG_BASE_DIRECTORY}/publickey"
server_private_key=$(sudo cat "${WG_BASE_DIRECTORY}/privatekey")

sudo cat <<EOF > "${WG_BASE_DIRECTORY}/wg0.conf"
[Interface]
PrivateKey = ${server_private_key}
Address = ${WG_ADDRESS_MASK}
ListenPort = ${WG_PORT}
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o ${WG_INTERFACE} -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o ${WG_INTERFACE} -j MASQUERADE

EOF

appendLineToFileIfNotExists /etc/sysctl.conf "net.ipv4.ip_forward=1"
sudo sysctl -p

sudo systemctl enable wg-quick@wg0.service
sudo systemctl start wg-quick@wg0.service

client_pub_key=$(sudo wg genkey | sudo tee "${WG_BASE_DIRECTORY}/client_privatekey" | sudo wg pubkey | sudo tee "${WG_BASE_DIRECTORY}/client_publickey")

sudo cat <<EOF >> "${WG_BASE_DIRECTORY}/wg0.conf"
[Peer]
PublicKey = ${client_pub_key}
AllowedIPs = ${WG_CLIENT_ALLOWED_IPS}

EOF

sudo systemctl restart wg-quick@wg0

echo "Server configuration is done."
