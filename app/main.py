import os
import stat
import logging
from fastapi import FastAPI, Depends, HTTPException, Header
from app.database.db_operations import create_database
from app.api import endpoints, instance_operations
from app.database.database_queries import router as database_router
from app.config import API_HASH

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application")
    create_database()
    
    # 确保 buildone.sh 有执行权限
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    shell_dir = os.path.join(app_dir, "shell")
    buildone_path = os.path.join(shell_dir, "buildone.sh")
    
    if os.path.exists(buildone_path):
        current_permissions = os.stat(buildone_path).st_mode
        os.chmod(buildone_path, current_permissions | stat.S_IEXEC)
        logger.info(f"Set execute permissions for {buildone_path}")
    else:
        logger.warning(f"buildone.sh not found at {buildone_path}")
    
    logger.info("Startup complete")

def verify_api_hash(accesshash: str = Header(...)):
    if accesshash != API_HASH:
        raise HTTPException(status_code=403, detail="Invalid API hash")
    return accesshash

# 包含现有的路由，添加hash验证
app.include_router(endpoints.router, dependencies=[Depends(verify_api_hash)])
app.include_router(instance_operations.router, dependencies=[Depends(verify_api_hash)])
app.include_router(database_router, prefix="/db", tags=["database"], dependencies=[Depends(verify_api_hash)])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=80, reload=True)


