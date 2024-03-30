## Debian 12

Params:
- interface: `ens4`

```bash
sudo dhclient -r ens4
sudo dhclient ens4

```


### Install Docker

https://docs.docker.com/engine/install/debian/#install-using-the-repository

```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

## Install Wireguard Server

https://t.me/t0digital/32

```bash
#!/bin/bash

set -e

sudo apt install -y wireguard

sudo wg genkey | sudo tee /etc/wireguard/privatekey | sudo wg pubkey | sudo tee /etc/wireguard/publickey
server_private_key=$(sudo cat /etc/wireguard/privatekey)

sudo cat <<EOF > /etc/wireguard/wg0.conf
[Interface]
PrivateKey = $server_private_key
Address = 10.0.0.1/24
ListenPort = 51830
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o ens4 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o ens4 -j MASQUERADE

EOF

sudo echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sudo sysctl -p

sudo systemctl enable wg-quick@wg0.service
sudo systemctl start wg-quick@wg0.service

client_pub_key=$(sudo wg genkey | sudo tee /etc/wireguard/client_privatekey | sudo wg pubkey | sudo tee /etc/wireguard/client_publickey)

sudo cat <<EOF >> /etc/wireguard/wg0.conf
[Peer]
PublicKey = $client_pub_key
AllowedIPs = 10.0.0.2/32

EOF

sudo systemctl restart wg-quick@wg0
```


```bash
#!/bin/bash

set -e

client_private_key=$(sudo cat /etc/wireguard/client_privatekey)
server_pub_key=$(sudo cat /etc/wireguard/publickey)

sudo cat <<EOF >> ~/client_wg.conf
[Interface]
PrivateKey = $client_private_key
Address = 10.0.0.2/32
DNS = 8.8.8.8

[Peer]
PublicKey = $server_pub_key
Endpoint = 192.168.1.122:51830
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 20
EOF
```

