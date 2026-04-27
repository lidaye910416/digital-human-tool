import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 数据目录
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
AVATARS_DIR = DATA_DIR / "avatars"
VIDEOS_DIR = DATA_DIR / "videos"
TEMPLATES_DIR = DATA_DIR / "templates"

# MiniMax API 配置
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimax.chat/v1"

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/database.db")

# 确保目录存在
for directory in [DATA_DIR, UPLOADS_DIR, AVATARS_DIR, VIDEOS_DIR, TEMPLATES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# 验证配置
def validate_config():
    errors = []
    if not MINIMAX_API_KEY:
        errors.append("MINIMAX_API_KEY is not set. Please set it in .env file.")
    if len(MINIMAX_API_KEY) < 10:
        errors.append("MINIMAX_API_KEY appears to be invalid (too short).")
    return errors
