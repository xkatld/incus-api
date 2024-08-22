import os
import stat
from fastapi import FastAPI
from app.database.db_operations import create_database
from app.api.endpoints import router

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    create_database()
    
    # 确保 buildone.sh 有执行权限
    app_dir = os.path.dirname(os.path.abspath(__file__))
    shell_dir = os.path.join(app_dir, "shell")
    buildone_path = os.path.join(shell_dir, "buildone.sh")
    current_permissions = os.stat(buildone_path).st_mode
    os.chmod(buildone_path, current_permissions | stat.S_IEXEC)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
