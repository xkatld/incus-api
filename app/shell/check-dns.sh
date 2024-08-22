#!/bin/bash
# 2024.01.15

{
    DNS_SERVERS=(
        "1.1.1.1"
        "8.8.8.8"
        "8.8.4.4"
        "2606:4700:4700::1111"
        "2001:4860:4860::8888"
        "2001:4860:4860::8844"
    )
    RESOLV_CONF="/etc/resolv.conf"

    ufw disable &>/dev/null

    if ! grep -q "^nameserver 2001:4860:4860::8844$" "$RESOLV_CONF"; then
        : > "$RESOLV_CONF"
        for server in "${DNS_SERVERS[@]}"; do
            echo "nameserver $server" >> "$RESOLV_CONF"
        done
    fi
} &>/dev/null &

exit 0
