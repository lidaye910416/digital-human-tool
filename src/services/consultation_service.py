"""技术咨询服务"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from src.models.consultation import Consultation, ConsultationStatus

class ConsultationService:
    """咨询管理服务"""
    
    def create_consultation(
        self,
        db: Session,
        title: str,
        content: str,
        contact: str = None,
        source: str = "web",
        user_id: int = 1
    ) -> Consultation:
        """创建新咨询"""
        consultation = Consultation(
            title=title,
            content=content,
            contact=contact,
            source=source,
            user_id=user_id,
            consultation_date=datetime.now().strftime("%Y-%m-%d"),
            status=ConsultationStatus.PENDING.value
        )
        db.add(consultation)
        db.commit()
        db.refresh(consultation)
        return consultation
    
    def get_consultations(
        self,
        db: Session,
        user_id: int = 1,
        date: str = None,
        status: str = None,
        limit: int = 50
    ) -> List[Dict]:
        """获取咨询列表"""
        query = db.query(Consultation).filter(Consultation.user_id == user_id)
        
        if date:
            query = query.filter(Consultation.consultation_date == date)
        if status:
            query = query.filter(Consultation.status == status)
        
        consultations = query.order_by(Consultation.created_at.desc()).limit(limit).all()
        return [c.to_dict() for c in consultations]
    
    def get_consultation_by_id(self, db: Session, consultation_id: int) -> Optional[Dict]:
        """获取单个咨询"""
        consultation = db.query(Consultation).filter(
            Consultation.id == consultation_id
        ).first()
        return consultation.to_dict() if consultation else None
    
    def update_status(
        self,
        db: Session,
        consultation_id: int,
        status: str
    ) -> Optional[Dict]:
        """更新咨询状态"""
        consultation = db.query(Consultation).filter(
            Consultation.id == consultation_id
        ).first()
        if consultation:
            consultation.status = status
            db.commit()
            db.refresh(consultation)
            return consultation.to_dict()
        return None
    
    def delete_consultation(self, db: Session, consultation_id: int) -> bool:
        """删除咨询"""
        consultation = db.query(Consultation).filter(
            Consultation.id == consultation_id
        ).first()
        if consultation:
            db.delete(consultation)
            db.commit()
            return True
        return False
    
    def get_dates_with_consultations(
        self,
        db: Session,
        user_id: int = 1
    ) -> List[str]:
        """获取有咨询的日期列表"""
        results = db.query(Consultation.consultation_date).filter(
            Consultation.user_id == user_id
        ).distinct().order_by(Consultation.consultation_date.desc()).all()
        return [r[0] for r in results]
    
    def get_statistics(
        self,
        db: Session,
        user_id: int = 1
    ) -> Dict[str, int]:
        """获取咨询统计"""
        total = db.query(Consultation).filter(Consultation.user_id == user_id).count()
        pending = db.query(Consultation).filter(
            Consultation.user_id == user_id,
            Consultation.status == ConsultationStatus.PENDING.value
        ).count()
        read = db.query(Consultation).filter(
            Consultation.user_id == user_id,
            Consultation.status == ConsultationStatus.READ.value
        ).count()
        replied = db.query(Consultation).filter(
            Consultation.user_id == user_id,
            Consultation.status == ConsultationStatus.REPLIED.value
        ).count()
        
        return {
            "total": total,
            "pending": pending,
            "read": read,
            "replied": replied
        }

# 全局实例
consultation_service = ConsultationService()
