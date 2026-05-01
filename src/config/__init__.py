"""
配置模块

统一管理所有配置
"""

import os
from pathlib import Path

# ===== 基础路径配置 =====

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
AUDIO_DIR = DATA_DIR / "audio"

# ===== API 配置 =====

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimax.chat/v1"

# ===== 数据库配置 =====

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/database.db")

# 确保目录存在
for directory in [DATA_DIR, AUDIO_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ===== 新闻源配置 =====

from src.config.sources import (
    RSS_SOURCES_ZH, RSS_SOURCES_EN, RSS_SOURCES,
    WEB_SITES, API_SOURCES, CATEGORIES,
    UNRELATED_KEYWORDS, SOURCE_TIERS, get_sources,
    get_categories, get_source_tiers, get_filter_keywords,
    get_quality_keywords, get_tier_for_source,
    QUALITY_KEYWORDS, COMPLETENESS_PATTERNS, DENSITY_PATTERNS
)

# ===== 配置验证 =====

def validate_config():
    """验证配置"""
    errors = []
    if not MINIMAX_API_KEY:
        errors.append("MINIMAX_API_KEY is not set")
    return errors

__all__ = [
    # 基础路径
    'BASE_DIR', 'DATA_DIR', 'AUDIO_DIR',
    # API
    'MINIMAX_API_KEY', 'MINIMAX_BASE_URL',
    # 数据库
    'DATABASE_URL', 'validate_config',
    # 新闻源
    'RSS_SOURCES_ZH', 'RSS_SOURCES_EN', 'RSS_SOURCES',
    'WEB_SITES', 'API_SOURCES', 'CATEGORIES',
    'UNRELATED_KEYWORDS', 'SOURCE_TIERS', 'get_sources',
    # 配置访问函数
    'get_categories', 'get_source_tiers', 'get_filter_keywords',
    'get_quality_keywords', 'get_tier_for_source',
    # 评分配置
    'QUALITY_KEYWORDS', 'COMPLETENESS_PATTERNS', 'DENSITY_PATTERNS'
]
