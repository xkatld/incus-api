from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.models.container import Container

DATABASE_URL = "sqlite:///./containers.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ContainerModel(Base):
    __tablename__ = "containers"

    id = Column(Integer, primary_key=True, index=True)
    server_name = Column(String, unique=True, index=True)
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

def create_database():
    Base.metadata.create_all(bind=engine)

def save_container(container: Container):
    db = SessionLocal()
    db_container = ContainerModel(**container.dict())
    db.add(db_container)
    db.commit()
    db.refresh(db_container)
    db.close()

def get_container(server_name: str):
    db = SessionLocal()
    container = db.query(ContainerModel).filter(ContainerModel.server_name == server_name).first()
    db.close()
    if container:
        return Container.from_orm(container)
    return None
