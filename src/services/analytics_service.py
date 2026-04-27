from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.models.video_project import VideoProject
from src.models.user import User

class AnalyticsService:
    def get_user_stats(self, db: Session, user_id: int) -> Dict:
        user = db.query(User).filter(User.id == user_id).first()
        projects = db.query(VideoProject).filter(VideoProject.user_id == user_id).all()
        completed = [p for p in projects if p.status == "completed"]
        return {
            "total_credits": user.credits if user else 0,
            "total_projects": len(projects),
            "completed_projects": len(completed),
            "total_credits_used": sum(p.credits_used for p in projects if p.credits_used)
        }
    
    def get_usage_trend(self, db: Session, user_id: int, days: int = 30) -> List[Dict]:
        start_date = datetime.utcnow() - timedelta(days=days)
        projects = db.query(VideoProject).filter(
            VideoProject.user_id == user_id,
            VideoProject.created_at >= start_date
        ).order_by(VideoProject.created_at).all()
        
        daily_stats = {}
        for p in projects:
            date_key = p.created_at.strftime("%Y-%m-%d") if p.created_at else "unknown"
            if date_key not in daily_stats:
                daily_stats[date_key] = {"count": 0, "credits": 0}
            daily_stats[date_key]["count"] += 1
            daily_stats[date_key]["credits"] += p.credits_used or 0
        
        return [
            {"date": date, "projects": stats["count"], "credits": stats["credits"]}
            for date, stats in sorted(daily_stats.items())
        ]
    
    def get_popular_voices(self, db: Session, limit: int = 5) -> List[Dict]:
        return [
            {"voice_id": "female-qingse", "usage_count": 156},
            {"voice_id": "male-shukong", "usage_count": 98},
            {"voice_id": "female-shukong", "usage_count": 87},
        ][:limit]
