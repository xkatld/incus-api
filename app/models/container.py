from pydantic import BaseModel
from typing import Optional
from enum import Enum

class ContainerStatus(str, Enum):
    START = "start"
    STOP = "stop"
    PAUSE = "pause"
    DELETE = "delete"

class ContainerCreate(BaseModel):
    cpu: int
    memory: int
    disk: int
    download_speed: int
    upload_speed: int
    ipv6: str
    system: str

class Container(BaseModel):
    server_name: str
    cpu: int
    memory: int
    disk: int
    ssh_port: int
    port_start: int
    port_end: int
    download_speed: int
    upload_speed: int
    ipv6: str
    system: str
    password: str
    status: ContainerStatus = ContainerStatus.START

    class Config:
        from_attributes = True
        # 移除 orm_mode = True，因为 from_attributes 已经足够了

class ContainerUpdate(BaseModel):
    cpu: Optional[int] = None
    memory: Optional[int] = None
    disk: Optional[int] = None
    download_speed: Optional[int] = None
    upload_speed: Optional[int] = None
    ipv6: Optional[str] = None
    system: Optional[str] = None
    status: Optional[ContainerStatus] = None
