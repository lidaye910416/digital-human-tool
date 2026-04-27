from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.api.routes import router as api_router
import os

app = FastAPI(title="Tech Echo - 科技资讯播报", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
@app.on_event("startup")
async def startup_event():
    from src.models.database import init_db
    init_db()

    # 启动定时调度器
    try:
        from src.services.scheduler_service import start_scheduler
        start_scheduler()
    except ImportError:
        pass  # APScheduler 未安装

@app.on_event("shutdown")
async def shutdown_event():
    from src.services.scheduler_service import stop_scheduler
    try:
        stop_scheduler()
    except:
        pass

# 注册 API 路由
app.include_router(api_router)

# 挂载静态文件目录 (用于头像图片)
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
if os.path.exists(data_dir):
    app.mount("/data", StaticFiles(directory=data_dir), name="data")

@app.get("/")
async def root():
    return {
        "name": "Tech Echo API",
        "version": "0.2.0",
        "description": "科技资讯播报平台 API"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
