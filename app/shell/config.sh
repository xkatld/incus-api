#!/bin/bash
# from https://github.com/oneclickvirt/incus
# 2023.06.29 optimized

# 系统识别
REGEX=("debian" "ubuntu" "centos|red hat|kernel|oracle linux|alma|rocky" "fedora" "alpine" "arch" "openwrt")
RELEASE=("Debian" "Ubuntu" "CentOS" "Fedora" "Alpine" "Arch" "OpenWrt")

CMD=("$(grep -i pretty_name /etc/os-release 2>/dev/null | cut -d \" -f2)")
SYS="${CMD[0]}"
for ((int = 0; int < ${#REGEX[@]}; int++)); do
    if [[ $(echo "$SYS" | tr '[:upper:]' '[:lower:]') =~ ${REGEX[int]} ]]; then
        SYSTEM="${RELEASE[int]}"
        [[ -n $SYSTEM ]] && break
    fi
done

# 定义需要阻止的包
PACKAGES="zmap nmap masscan medusa apache2-utils hping3"

# 阻止包安装的函数
block_package() {
    local pkg=$1
    echo '#!/bin/bash\nexit 1' | sudo tee "/usr/local/sbin/${pkg}-install" > /dev/null
    sudo chmod +x "/usr/local/sbin/${pkg}-install"
    if command -v dpkg > /dev/null; then
        sudo ln -sf "/usr/local/sbin/${pkg}-install" "/var/lib/dpkg/info/${pkg}.postinst"
    elif command -v rpm > /dev/null; then
        sudo ln -sf "/usr/local/sbin/${pkg}-install" "/var/lib/rpm/scripts/${pkg}.postinst"
    fi
}

# 根据系统执行相应操作
case $SYSTEM in
    Debian|Ubuntu)
        echo "Package: $PACKAGES
Pin: release *
Pin-Priority: -1" | sudo tee -a /etc/apt/preferences > /dev/null

        for pkg in $PACKAGES; do
            block_package "$pkg"
        done
        echo "Packages blocked on $SYSTEM: $PACKAGES"
        ;;
    CentOS|Fedora)
        echo "RPM-based system detected. No action taken as these packages are typically not available."
        ;;
    Alpine|Arch|OpenWrt)
        echo "$SYSTEM detected. This script is not designed for this system."
        ;;
    *)
        echo "Unsupported system: $SYS"
        ;;
esac

# 删除脚本自身
rm -f "$0"
