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
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
~~~
# api示例
~~~
创建服务器api：
curl -X POST "http://xxx:8080/containers/" -H "Content-Type: application/json" -d '{"cpu": 2, "memory": 1024, "disk": 20, "download_speed": 100, "upload_speed": 10, "ipv6": "N", "system": "debian11"}' -H "accesshash: xxx"
关机服务器api：
curl -X POST "http://localhost:8000/instances/$name/start" -H "accesshash: xxx"
开机服务器api：
curl -X POST "http://localhost:8000/instances/$name/stop" -H "accesshash: xxx"
重启服务器api：
curl -X POST "http://localhost:8000/instances/$name/restart" -H "accesshash: xxx"
删除服务器api：
curl -X POST "http://localhost:8000/instances/$name/delete" -H "accesshash: xxx"
暂停服务器api：
curl -X POST "http://localhost:8000/instances/$name/pause" -H "accesshash: xxx"
恢复服务器api：
curl -X POST "http://localhost:8000/instances/$name/resume" -H "accesshash: xxx"
查询服务器:
curl -X GET "http://xxx:xxx/db/containers" -H "accesshash: xxx"
查询单个服务器：
curl -X GET "http://xxx:xxx/db/containers/$name" -H "accesshash: xxx"
~~~
