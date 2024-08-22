import os
import subprocess
import random
import string
from fastapi import APIRouter, HTTPException
from app.database.db_operations import save_container, get_container
from app.models.container import Container, ContainerCreate

router = APIRouter()

def generate_random_name():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def generate_random_ssh_port():
    return random.randint(1001, 2000)

def generate_random_port_range():
    start = random.randint(3001, 7900)
    end = start + 99
    return start, end

@router.post("/containers/")
async def create_container(container: ContainerCreate):
    server_name = generate_random_name()
    ssh_port = generate_random_ssh_port()
    port_start, port_end = generate_random_port_range()

    # 获取 shell 目录的路径
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    shell_dir = os.path.join(app_dir, "shell")
    buildone_path = os.path.join(shell_dir, "buildone.sh")

    cmd = [
        buildone_path,
        server_name,
        str(container.cpu),
        str(container.memory),
        str(container.disk),
        str(ssh_port),
        str(port_start),
        str(port_end),
        str(container.download_speed),
        str(container.upload_speed),
        container.ipv6,
        container.system
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        output = result.stdout.strip().split()
        if len(output) != 5:
            raise ValueError("Unexpected output format from buildone.sh")
        
        name, sshn, passwd, nat1, nat2 = output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Failed to create container: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    new_container = Container(
        server_name=name,
        cpu=container.cpu,
        memory=container.memory,
        disk=container.disk,
        ssh_port=int(sshn),
        port_start=int(nat1),
        port_end=int(nat2),
        download_speed=container.download_speed,
        upload_speed=container.upload_speed,
        ipv6=container.ipv6,
        system=container.system,
        password=passwd
    )

    save_container(new_container)

    return {"message": "Container created successfully", "container": new_container}

@router.get("/containers/{server_name}")
async def read_container(server_name: str):
    container = get_container(server_name)
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    return container
