#!/bin/bash
# by https://github.com/oneclickvirt/incus
# 2024.08.21 优化版本

if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be executed with root privileges."
  exit 1
fi

# 检查SSH是否已安装
if command -v sshd &> /dev/null; then
    echo "SSH server is already installed. Skipping installation."
    SSH_INSTALLED=true
else
    SSH_INSTALLED=false
fi

# 系统识别（仅在需要安装SSH时使用）
if [ "$SSH_INSTALLED" = false ]; then
    REGEX=("debian" "ubuntu" "centos|red hat|kernel|oracle linux|alma|rocky" "fedora" "alpine" "arch" "openwrt")
    RELEASE=("Debian" "Ubuntu" "CentOS" "Fedora" "Alpine" "Arch" "OpenWrt")
    PACKAGE_UPDATE=("apt-get update" "apt-get update" "yum -y update" "yum -y update" "apk update" "pacman -Sy" "opkg update")
    PACKAGE_INSTALL=("apt-get -y install" "apt-get -y install" "yum -y install" "yum -y install" "apk add --no-cache" "pacman -S --noconfirm" "opkg install")

    CMD=("$(grep -i pretty_name /etc/os-release 2>/dev/null | cut -d \" -f2)")
    SYS="${CMD[0]}"
    for ((int = 0; int < ${#REGEX[@]}; int++)); do
        if [[ $(echo "$SYS" | tr '[:upper:]' '[:lower:]') =~ ${REGEX[int]} ]]; then
            SYSTEM="${RELEASE[int]}"
            [[ -n $SYSTEM ]] && break
        fi
    done
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

# 安装SSH（如果需要）
install_ssh_if_needed() {
    if [ "$SSH_INSTALLED" = false ]; then
        ${PACKAGE_UPDATE[int]}
        ${PACKAGE_INSTALL[int]} openssh-server
    fi
}

# 设置root密码
set_root_password() {
    echo root:"$1" | chpasswd root
}

# 主要操作
install_ssh_if_needed
update_ssh_config
update_dns
set_root_password "$1"

# 重启SSH服务
if command -v systemctl &> /dev/null; then
    systemctl restart sshd || systemctl restart ssh
elif command -v service &> /dev/null; then
    service sshd restart || service ssh restart
else
    echo "Unable to restart SSH service. Please restart it manually."
fi

# 删除脚本自身
rm -f "$0"
