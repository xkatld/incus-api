#!/bin/sh
# by https://github.com/oneclickvirt/incus
# 精简版本（保留DNS设置）

if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be executed with root privileges."
  exit 1
fi

# 识别系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "无法识别操作系统"
    exit 1
fi

# 修改DNS设置
update_dns() {
    if [ -f "/etc/resolv.conf" ]; then
        cp /etc/resolv.conf /etc/resolv.conf.bak
        echo "nameserver 8.8.8.8" | tee /etc/resolv.conf >/dev/null
        echo "nameserver 8.8.4.4" | tee -a /etc/resolv.conf >/dev/null
    fi
}

# 更新SSH配置
update_ssh_config() {
    if [ -f "/etc/ssh/sshd_config" ]; then
        sed -i '/^#PermitRootLogin\|PermitRootLogin/c PermitRootLogin yes' /etc/ssh/sshd_config
        sed -i "s/^#\?PasswordAuthentication.*/PasswordAuthentication yes/g" /etc/ssh/sshd_config
        sed -i 's/#ListenAddress 0.0.0.0/ListenAddress 0.0.0.0/' /etc/ssh/sshd_config
        sed -i 's/#ListenAddress ::/ListenAddress ::/' /etc/ssh/sshd_config
        sed -i '/^#AddressFamily\|AddressFamily/c AddressFamily any' /etc/ssh/sshd_config
        sed -i "s/^#\?\(Port\).*/\1 22/" /etc/ssh/sshd_config
    fi
}

# 设置root密码
set_root_password() {
    if [ "$OS" = "alpine" ]; then
        echo root:"$1" | chpasswd root
    elif [ "$OS" = "openwrt" ]; then
        echo -e "$1\n$1" | passwd root
    fi
}

# 主要操作
case $OS in
    alpine)
        apk update
        apk add --no-cache openssh-server
        ssh-keygen -A
        update_ssh_config
        rc-update add sshd default
        service sshd start
        ;;
    openwrt)
        opkg update
        opkg install openssh-server
        /etc/init.d/sshd enable
        update_ssh_config
        /etc/init.d/sshd start
        ;;
    *)
        echo "不支持的操作系统"
        exit 1
        ;;
esac

update_dns
set_root_password "$1"

# 删除脚本自身
rm -f "$0"
