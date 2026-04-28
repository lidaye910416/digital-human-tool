"""
TechEcho Pro - 新闻 API 端点

提供新闻相关的 API 接口
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
import json
import os

router = APIRouter(prefix="/api/news", tags=["news"])

DATA_PATH = os.path.join(os.path.dirname(__file__), '../../app/data/news.json')

@router.get("/")
async def get_news(
    lang: Optional[str] = None,
    category: Optional[str] = None,
    min_quality: Optional[int] = 55
):
    """获取新闻列表"""
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        news = data.get('news', [])
        
        # 过滤
        if lang:
            news = [n for n in news if n.get('lang') == lang]
        if category and category != 'all':
            news = [n for n in news if n.get('category') == category]
        if min_quality:
            news = [n for n in news if n.get('quality', {}).get('total_100', 0) >= min_quality]
        
        return {
            'success': True,
            'data': news,
            'total': len(news)
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="News data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/collect")
async def trigger_collect():
    """触发新闻收集任务"""
    # 这是一个预留端点，实际收集需要调用 scripts/collect_news.py
    return {
        'success': True,
        'message': 'Collection task triggered. Use CLI: python scripts/collect_news.py',
        'endpoints': {
            'cli': 'python scripts/collect_news.py',
            'schedule': '设置定时任务调用 CLI'
        }
    }

@router.get("/stats")
async def get_stats():
    """获取新闻统计"""
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            'success': True,
            'lastUpdate': data.get('lastUpdate'),
            'totalCount': data.get('totalCount'),
            'stats': data.get('stats'),
            'categories': data.get('categories', [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{news_id}")
async def get_news_detail(news_id: str):
    """获取新闻详情"""
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        news = data.get('news', [])
        item = next((n for n in news if n.get('id') == news_id), None)
        
        if not item:
            raise HTTPException(status_code=404, detail="News not found")
        
        return {
            'success': True,
            'data': item
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
