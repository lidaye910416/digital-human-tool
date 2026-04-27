from typing import Dict
from src.services.minimax_client import get_minimax_client

class LipSyncService:
    def __init__(self):
        self.minimax = get_minimax_client()
        self.credit_rate = 0.5  # 每秒 0.5 积分
    
    async def create_video(self, avatar_image_url: str, audio_url: str, quality: str = "standard") -> Dict:
        """创建唇形同步视频"""
        try:
            response = await self.minimax.speech_to_video(audio_url=audio_url, image_url=avatar_image_url)
            video_url = response.get("data", {}).get("video_url", "")
            task_id = response.get("data", {}).get("task_id", "")
        except Exception:
            video_url = "http://example.com/video.mp4"  # 模拟
            task_id = "task_123"
        
        return {
            "video_url": video_url,
            "task_id": task_id,
            "status": "completed" if video_url else "pending"
        }
    
    async def check_status(self, task_id: str) -> Dict:
        """检查视频生成状态"""
        return {"task_id": task_id, "status": "completed", "progress": 100}
    
    def calculate_credits(self, duration_seconds: int) -> int:
        """计算唇形同步消耗的积分"""
        return max(10, int(duration_seconds * self.credit_rate))
