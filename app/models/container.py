from pydantic import BaseModel

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

    class Config:
        orm_mode = True
