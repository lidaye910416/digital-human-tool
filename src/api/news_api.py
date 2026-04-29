"""
TechEcho Pro - 新闻 API 端点

提供新闻相关的 API 接口 - 从 news.json 读取双语新闻数据
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
import json
import os
from datetime import datetime

router = APIRouter(prefix="/news", tags=["news"])

DATA_PATH = os.path.join(os.path.dirname(__file__), '../../app/data/news.json')

def load_news_data():
    """加载新闻数据"""
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        return None

@router.get("")
async def get_news_list(
    lang: Optional[str] = Query(None, description="语言筛选: zh, en, both"),
    category: Optional[str] = Query(None, description="分类筛选"),
    date: Optional[str] = Query(None, description="日期筛选: YYYY-MM-DD"),
    min_quality: Optional[int] = Query(55, description="最低质量分")
):
    """获取新闻列表

    特殊逻辑: 如果请求今天但没有今天的新闻，自动返回昨天的新闻
    (因为新闻通常在当天上午收集，但内容是昨天的)
    """
    data = load_news_data()
    if not data:
        raise HTTPException(status_code=404, detail="News data not found")

    news = data.get('news', [])
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - __import__('datetime').timedelta(days=1)).strftime('%Y-%m-%d')

    # 日期过滤
    if date:
        # 检查请求的日期是否有新闻
        date_news = [n for n in news if n.get('published_at', '').startswith(date)]
        if date_news:
            news = date_news
        elif date == today and yesterday:
            # 今天没有新闻，返回昨天的
            date_news = [n for n in news if n.get('published_at', '').startswith(yesterday)]
            if date_news:
                news = date_news
        else:
            news = []

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

@router.get("/dates")
async def get_available_dates():
    """获取有新闻的日期列表

    逻辑:
    - 返回新闻实际发布日期
    - 如果最新新闻是昨天(非今天), 添加"今天"作为选项
      (因为新闻通常在当天上午收集, 但内容是昨天的)
    """
    data = load_news_data()
    if not data:
        return {'success': True, 'data': []}

    # 从 news.json 提取日期
    news = data.get('news', [])
    dates = set()
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - __import__('datetime').timedelta(days=1)).strftime('%Y-%m-%d')

    for item in news:
        published_at = item.get('published_at', '')
        if published_at:
            date_str = published_at.split(' ')[0] if ' ' in published_at else published_at[:10]
            if len(date_str) == 10:
                dates.add(date_str)

    # 如果最新新闻是昨天但没有今天的新闻, 添加"今天"选项
    if dates and yesterday in dates and today not in dates:
        dates.add(today)

    return {
        'success': True,
        'data': sorted(list(dates), reverse=True)
    }

@router.get("/stats")
async def get_stats():
    """获取新闻统计"""
    data = load_news_data()
    if not data:
        return JSONResponse({
            'success': True,
            'data': {
                'lastUpdate': None,
                'totalCount': 0,
                'stats': {'A+': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0},
                'categories': []
            }
        })

    return {
        'success': True,
        'data': {
            'lastUpdate': data.get('lastUpdate'),
            'totalCount': data.get('totalCount', 0),
            'stats': data.get('stats', {}),
            'categories': data.get('categories', [])
        }
    }

@router.get("/categories")
async def get_categories():
    """获取资讯分类"""
    data = load_news_data()
    categories = data.get('categories', []) if data else []

    CATEGORY_MAP = {
        'ai': {'name': 'AI', 'emoji': '🤖'},
        'tools': {'name': '工具', 'emoji': '🔧'},
        'news': {'name': '动态', 'emoji': '📰'},
        'product': {'name': '产品', 'emoji': '💡'}
    }

    result = []
    for cat in categories:
        info = CATEGORY_MAP.get(cat, {'name': cat, 'emoji': '📰'})
        result.append({
            'id': cat,
            'name': info['name'],
            'emoji': info['emoji']
        })

    return {
        'success': True,
        'data': result
    }

@router.get("/{news_id}")
async def get_news_detail(news_id: str):
    """获取新闻详情"""
    data = load_news_data()
    if not data:
        raise HTTPException(status_code=404, detail="News data not found")

    news = data.get('news', [])
    item = next((n for n in news if n.get('id') == news_id), None)

    if not item:
        raise HTTPException(status_code=404, detail="News not found")

    return {
        'success': True,
        'data': item
    }

@router.post("/collect")
async def trigger_collect():
    """触发新闻收集任务"""
    return {
        'success': True,
        'message': 'Collection task triggered. Use CLI: python scripts/collect_news.py',
        'endpoints': {
            'cli': 'python scripts/collect_news.py',
            'schedule': '设置定时任务调用 CLI'
        }
    }

@router.post("/{news_id}/read")
async def read_news_aloud(
    news_id: str,
    voice_id: str = Query("female-tianmei")
):
    """朗读新闻 - 预留接口"""
    return {
        'success': True,
        'message': 'TTS 功能预留',
        'data': {
            'news_id': news_id,
            'audio_url': None,
            'voice_id': voice_id
        }
    }

@router.put("/{news_id}/read")
async def mark_as_read(news_id: str):
    """标记新闻为已读 - 预留接口"""
    return {"success": True, "message": "Marked as read"}
