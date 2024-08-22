# incus-api
incus功能性api
~~~
apt install git python3 python3-pip
rm /usr/lib/python3.11/EXTERNALLY-MANAGED
git clone https://github.com/xkatld/incus-api.git
chmod 777 ./incus-api/shell/*
cp ./incus-api/shell/* /usr/local/bin/
~~~
首先安装incus
~~~
bash ./incus-api/app/shell/buildone.sh
~~~
安装python3依赖
~~~
pip install -r ./incus-api/requirements.txt
~~~
