from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.db_operations import get_db, ContainerModel
from app.models.container import Container

router = APIRouter()

@router.get("/containers", response_model=List[Container])
async def get_all_containers(db: Session = Depends(get_db)):
    containers = db.query(ContainerModel).all()
    return [Container.from_orm(container) for container in containers]

@router.get("/containers/{server_name}", response_model=Container)
async def get_container_by_name(server_name: str, db: Session = Depends(get_db)):
    container = db.query(ContainerModel).filter(ContainerModel.server_name == server_name).first()
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    return Container.from_orm(container)
