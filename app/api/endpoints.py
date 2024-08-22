import os
import re
import subprocess
import random
import string
import logging
from fastapi import APIRouter, HTTPException
from app.database.db_operations import save_or_update_container, get_container, update_container
from app.models.container import Container, ContainerCreate, ContainerUpdate, ContainerStatus

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout + result.stderr
        
        pattern = r'(\w+)\s+(\d+)\s+(\w+)\s+(\d+)\s+(\d+)'
        match = re.search(pattern, output)
        
        if not match:
            raise ValueError("Unable to extract container information from output")
        
        name, sshn, passwd, nat1, nat2 = match.groups()
    except subprocess.CalledProcessError as e:
        output = e.stdout + e.stderr
        pattern = r'(\w+)\s+(\d+)\s+(\w+)\s+(\d+)\s+(\d+)'
        match = re.search(pattern, output)
        if match:
            name, sshn, passwd, nat1, nat2 = match.groups()
        else:
            error_message = f"Failed to create container. Output: {output}"
            raise HTTPException(status_code=500, detail=error_message)
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
        password=passwd,
        status=ContainerStatus.START
    )

    try:
        logger.info(f"Attempting to save container: {new_container.server_name}")
        saved_container = save_or_update_container(new_container)
        logger.info(f"Container saved successfully: {saved_container.server_name}")
    except ValueError as e:
        logger.error(f"Error saving container: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error saving container: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

    return {"message": "Container created successfully", "container": saved_container}

@router.get("/containers/{server_name}")
async def read_container(server_name: str):
    container = get_container(server_name)
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    return container

@router.put("/containers/{server_name}")
async def update_container_config(server_name: str, container_update: ContainerUpdate):
    updated_container = update_container(server_name, container_update.dict(exclude_unset=True))
    if updated_container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    return {"message": "Container updated successfully", "container": updated_container}
