from sqlalchemy import create_engine, Column, Integer, String, Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from app.models.container import Container, ContainerStatus

DATABASE_URL = "sqlite:///./containers.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ContainerModel(Base):
    __tablename__ = "containers"

    server_name = Column(String, primary_key=True, index=True)
    cpu = Column(Integer)
    memory = Column(Integer)
    disk = Column(Integer)
    ssh_port = Column(Integer, unique=True)
    port_start = Column(Integer)
    port_end = Column(Integer)
    download_speed = Column(Integer)
    upload_speed = Column(Integer)
    ipv6 = Column(String)
    system = Column(String)
    password = Column(String)
    status = Column(SQLAlchemyEnum(ContainerStatus), default=ContainerStatus.START)

def create_database():
    Base.metadata.create_all(bind=engine)

def save_or_update_container(container: Container):
    db = SessionLocal()
    try:
        db_container = db.query(ContainerModel).filter(ContainerModel.server_name == container.server_name).first()
        if db_container:
            # Update existing container
            for key, value in container.dict().items():
                setattr(db_container, key, value)
        else:
            # Create new container
            db_container = ContainerModel(**container.dict())
            db.add(db_container)
        db.commit()
        db.refresh(db_container)
    except IntegrityError:
        db.rollback()
        raise ValueError("Container with this name or SSH port already exists")
    finally:
        db.close()
    return container

def get_container(server_name: str):
    db = SessionLocal()
    container = db.query(ContainerModel).filter(ContainerModel.server_name == server_name).first()
    db.close()
    if container:
        return Container.from_orm(container)
    return None

def update_container(server_name: str, updated_data: dict):
    db = SessionLocal()
    db_container = db.query(ContainerModel).filter(ContainerModel.server_name == server_name).first()
    if db_container:
        for key, value in updated_data.items():
            setattr(db_container, key, value)
        db.commit()
        db.refresh(db_container)
        db.close()
        return Container.from_orm(db_container)
    db.close()
    return None

def update_container_status(server_name: str, status: ContainerStatus):
    db = SessionLocal()
    try:
        db_container = db.query(ContainerModel).filter(ContainerModel.server_name == server_name).first()
        if db_container:
            db_container.status = status
            db.commit()
            db.refresh(db_container)
            return Container.from_orm(db_container)
        return None
    finally:
        db.close()
