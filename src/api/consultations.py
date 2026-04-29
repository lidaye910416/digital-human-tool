"""技术咨询 API 路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from src.models.database import get_db
from src.services.consultation_service import consultation_service
from src.services.minimax_client import get_minimax_client
from src.services.tts_service import TTSService as TextToSpeechService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/consultations", tags=["consultations"])

# ============ Request Models ============
class ConsultationCreate(BaseModel):
    title: str
    content: str
    contact: Optional[str] = None
    source: str = "web"
    user_id: int = 1

class ConsultationUpdate(BaseModel):
    status: Optional[str] = None
    avatar_id: Optional[int] = None
    voice_id: Optional[str] = None

class ConsultationReadRequest(BaseModel):
    consultation_id: int
    voice_id: str = "female-tianmei"
    user_id: int = 1

# ============ API Endpoints ============

@router.post("")
def create_consultation(
    request: ConsultationCreate,
    db: Session = Depends(get_db)
):
    """创建新咨询"""
    consultation = consultation_service.create_consultation(
        db=db,
        title=request.title,
        content=request.content,
        contact=request.contact,
        source=request.source,
        user_id=request.user_id
    )
    return {"success": True, "data": consultation.to_dict()}

@router.get("")
def get_consultations(
    user_id: int = Query(1),
    date: Optional[str] = Query(None, description="筛选日期 YYYY-MM-DD"),
    status: Optional[str] = Query(None),
    limit: int = Query(50),
    db: Session = Depends(get_db)
):
    """获取咨询列表"""
    consultations = consultation_service.get_consultations(
        db=db,
        user_id=user_id,
        date=date,
        status=status,
        limit=limit
    )
    return {"success": True, "data": consultations}

@router.get("/dates")
def get_consultation_dates(
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """获取有咨询的日期列表"""
    dates = consultation_service.get_dates_with_consultations(db=db, user_id=user_id)
    return {"success": True, "data": dates}

@router.get("/statistics")
def get_statistics(
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """获取咨询统计"""
    stats = consultation_service.get_statistics(db=db, user_id=user_id)
    return {"success": True, "data": stats}

@router.get("/{consultation_id}")
def get_consultation(
    consultation_id: int,
    db: Session = Depends(get_db)
):
    """获取单个咨询详情"""
    consultation = consultation_service.get_consultation_by_id(db=db, consultation_id=consultation_id)
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    return {"success": True, "data": consultation}

@router.put("/{consultation_id}")
def update_consultation(
    consultation_id: int,
    request: ConsultationUpdate,
    db: Session = Depends(get_db)
):
    """更新咨询（状态、关联数字人/声音）"""
    update_data = {}
    if request.status:
        update_data["status"] = request.status
    
    if update_data:
        result = consultation_service.update_status(db=db, consultation_id=consultation_id, status=request.status)
        if not result:
            raise HTTPException(status_code=404, detail="Consultation not found")
        return {"success": True, "data": result}
    return {"success": True, "message": "No updates provided"}

@router.delete("/{consultation_id}")
def delete_consultation(
    consultation_id: int,
    db: Session = Depends(get_db)
):
    """删除咨询"""
    success = consultation_service.delete_consultation(db=db, consultation_id=consultation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Consultation not found")
    return {"success": True, "message": "Deleted successfully"}

@router.post("/{consultation_id}/read-aloud")
async def read_consultation_aloud(
    consultation_id: int,
    voice_id: str = Query("female-tianmei"),
    db: Session = Depends(get_db)
):
    """朗读咨询内容"""
    consultation = consultation_service.get_consultation_by_id(db=db, consultation_id=consultation_id)
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    
    # 构建朗读文本
    read_text = f"咨询标题：{consultation['title']}。咨询内容：{consultation['content']}"
    
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
                "consultation_id": consultation_id,
                "audio_url": result.get("audio_url", ""),
                "voice_id": voice_id
            }
        }
    except Exception as e:
        logger.error(f"TTS failed: {e}")
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")
