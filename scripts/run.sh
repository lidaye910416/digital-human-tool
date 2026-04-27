#!/bin/bash
set -e

# 设置环境变量
export MINIMAX_API_KEY="${MINIMAX_API_KEY:-your-api-key-here}"

# 初始化数据库
python -c "from src.models import init_db; init_db()"

# 初始化默认场景
python -c "
from src.models.database import SessionLocal
from src.services.scene_service import SceneService
db = SessionLocal()
service = SceneService()
service.init_default_scenes(db)
db.close()
print('Default scenes initialized')
"

# 启动服务
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
