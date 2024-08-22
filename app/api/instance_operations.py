import subprocess
import logging
from fastapi import APIRouter, HTTPException
from app.database.db_operations import update_container_status, get_container
from app.models.container import ContainerStatus

router = APIRouter()
logger = logging.getLogger(__name__)

def execute_incus_command(command: str, name: str) -> str:
    try:
        result = subprocess.run(['incus', command, name], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing incus command: {e.stderr}")
        raise HTTPException(status_code=500, detail=f"Failed to execute incus command: {e.stderr}")

def get_instance_status(name: str) -> ContainerStatus:
    try:
        result = subprocess.run(['incus', 'list', name, '--format', 'csv', '-c', 's'], capture_output=True, text=True, check=True)
        status = result.stdout.strip().lower()
        if status == "running":
            return ContainerStatus.START
        elif status == "stopped":
            return ContainerStatus.STOP
        elif status == "frozen":
            return ContainerStatus.PAUSE
        else:
            return ContainerStatus.STOP  # 默认返回 STOP 状态
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting instance status: {e.stderr}")
        raise HTTPException(status_code=500, detail=f"Failed to get instance status: {e.stderr}")

@router.post("/instances/{name}/{action}")
async def manage_instance(name: str, action: str):
    valid_actions = ["delete", "start", "stop", "restart", "pause", "resume"]
    if action not in valid_actions:
        raise HTTPException(status_code=400, detail="Invalid action")

    container = get_container(name)
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")

    if action == "delete":
        execute_incus_command("delete", name)
        update_container_status(name, ContainerStatus.DELETE)
        return {"message": f"Container {name} deleted successfully"}

    execute_incus_command(action, name)
    
    # 根据操作更新状态
    if action in ["start", "restart", "resume"]:
        new_status = ContainerStatus.START
    elif action == "stop":
        new_status = ContainerStatus.STOP
    elif action == "pause":
        new_status = ContainerStatus.PAUSE
    else:
        new_status = get_instance_status(name)

    update_container_status(name, new_status)

    return {"message": f"Action {action} executed successfully on {name}", "new_status": new_status}

@router.get("/instances/{name}/status")
async def get_instance_status_api(name: str):
    container = get_container(name)
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")

    status = get_instance_status(name)
    update_container_status(name, status)

    return {"name": name, "status": status}
