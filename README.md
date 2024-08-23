# incus-api
incus功能性api
~~~
apt install git python3 python3-pip
rm /usr/lib/python3.11/EXTERNALLY-MANAGED
git clone https://github.com/xkatld/incus-api.git
chmod 777 ./incus-api/app/shell/*
cp ./incus-api/app/shell/* /usr/local/bin/
~~~
首先安装incus
~~~
bash ./incus-api/app/shell/install_incus.sh
~~~
安装python3依赖
~~~
cd ./incus-api
pip install -r requirements.txt
~~~
运行
~~~
cd ./incus-api
uvicorn app.main:app --reload
~~~
# api示例
~~~
curl -X POST "http://localhost:8000/containers/" -H "Content-Type: application/json" -d '{"cpu": 2, "memory": 1024, "disk": 20, "download_speed": 100, "upload_speed": 10, "ipv6": "N", "system": "debian11"}'

curl -X POST "http://localhost:8000/instances/kd5pzzme/stop"
~~~
