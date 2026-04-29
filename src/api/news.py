"""科技资讯 API 路由 (已弃用 - 请使用 news_api.py)"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from src.models.database import get_db
# from src.services.news_collector import news_collector  # 已移除，向后兼容
from src.services.tts_service import TTSService as TextToSpeechService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/news", tags=["news"])

# ============ Request Models ============
class CollectRequest(BaseModel):
    target_date: Optional[str] = None  # YYYY-MM-DD，默认昨日

class NewsResponse(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    source_name: str
    category: str
    date_key: str
    score: float
    is_read: bool

# ============ API Endpoints ============

@router.get("")
async def get_news_list(
    date: Optional[str] = Query(None, description="日期 YYYY-MM-DD"),
    category: Optional[str] = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """获取资讯列表"""
    from src.models.news import NewsItem
    
    query = db.query(NewsItem)
    
    # 日期筛选
    if date:
        query = query.filter(NewsItem.date_key == date)
    else:
        # 默认返回最近7天
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        query = query.filter(NewsItem.date_key >= week_ago)
    
    # 分类筛选
    if category:
        query = query.filter(NewsItem.category == category)
    
    # 按评分和日期排序
    query = query.order_by(desc(NewsItem.score), desc(NewsItem.collected_at))
    
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    
    return {
        "success": True,
        "data": {
            "items": [item.to_dict() for item in items],
            "total": total,
            "offset": offset,
            "limit": limit
        }
    }

@router.get("/dates")
async def get_available_dates(
    limit: int = Query(30),
    db: Session = Depends(get_db)
):
    """获取有资讯的日期列表"""
    from src.models.news import NewsItem
    
    results = db.query(NewsItem.date_key).distinct().order_by(
        desc(NewsItem.date_key)
    ).limit(limit).all()
    
    return {
        "success": True,
        "data": [r[0] for r in results]
    }

@router.get("/stats")
async def get_news_stats(db: Session = Depends(get_db)):
    """获取资讯统计信息"""
    from src.models.news import NewsItem
    from sqlalchemy import func

    total = db.query(func.count(NewsItem.id)).scalar() or 0

    # 按分类统计
    category_stats = db.query(
        NewsItem.category,
        func.count(NewsItem.id).label('count')
    ).group_by(NewsItem.category).all()

    categories = [s[0] for s in category_stats]

    # 按评分统计 (简化版)
    stats = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0}
    all_news = db.query(NewsItem).all()
    for news in all_news:
        score = news.score
        if score >= 90:
            stats["A+"] = stats.get("A+", 0) + 1
        elif score >= 75:
            stats["A"] = stats.get("A", 0) + 1
        elif score >= 60:
            stats["B"] = stats.get("B", 0) + 1
        elif score >= 45:
            stats["C"] = stats.get("C", 0) + 1
        else:
            stats["D"] = stats.get("D", 0) + 1

    # 获取最后更新时间
    latest = db.query(NewsItem).order_by(desc(NewsItem.collected_at)).first()
    last_update = latest.collected_at.isoformat() if latest else None

    return {
        "success": True,
        "data": {
            "lastUpdate": last_update,
            "totalCount": total,
            "stats": stats,
            "categories": categories
        }
    }

@router.get("/categories")
async def get_categories():
    """获取资讯分类"""
    return {
        "success": True,
        "data": [
            {"id": "tech", "name": "科技", "emoji": "💻"},
            {"id": "ai", "name": "AI", "emoji": "🧠"},
            {"id": "web3", "name": "Web3", "emoji": "⛓️"},
            {"id": "crypto", "name": "加密货币", "emoji": "🪙"},
        ]
    }

@router.get("/{news_id}")
async def get_news_detail(
    news_id: int,
    db: Session = Depends(get_db)
):
    """获取资讯详情"""
    from src.models.news import NewsItem
    
    news = db.query(NewsItem).filter(NewsItem.id == news_id).first()
    
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # 标记为已读
    if not news.is_read:
        news.is_read = True
        db.commit()
    
    return {
        "success": True,
        "data": news.to_dict()
    }

@router.post("/collect")
async def trigger_collect(
    request: CollectRequest = None,
    db: Session = Depends(get_db)
):
    """手动触发资讯收集 (已弃用)"""
    raise HTTPException(status_code=410, detail="此接口已弃用，请使用 /api/news 端点获取新闻")

@router.post("/{news_id}/read")
async def read_news_aloud(
    news_id: int,
    voice_id: str = Query("female-tianmei"),
    db: Session = Depends(get_db)
):
    """朗读资讯"""
    from src.models.news import NewsItem
    
    news = db.query(NewsItem).filter(NewsItem.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # 构建朗读文本
    read_text = f"标题：{news.title}。来源：{news.source_name}。"
    if news.summary:
        read_text += f"内容摘要：{news.summary[:500]}"
    
    # 调用 TTS
    tts_service = TextToSpeechService()
    try:
        result = await tts_service.synthesize(
            text=read_text,
            voice_config={"voice_id": voice_id, "speed": 1.0}
        )
        
        return {
            "success": True,
            "data": {
                "news_id": news_id,
                "audio_url": result.get("audio_url", ""),
                "voice_id": voice_id
            }
        }
    except Exception as e:
        logger.error(f"TTS failed: {e}")
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

@router.put("/{news_id}/read")
async def mark_as_read(
    news_id: int,
    db: Session = Depends(get_db)
):
    """标记资讯为已读"""
    from src.models.news import NewsItem
    
    news = db.query(NewsItem).filter(NewsItem.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    news.is_read = True
    db.commit()
    
    return {"success": True, "message": "Marked as read"}
