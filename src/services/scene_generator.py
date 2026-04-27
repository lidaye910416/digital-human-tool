from typing import Dict, Optional
from sqlalchemy.orm import Session
from src.services.minimax_client import get_minimax_client
from src.models.scene import Scene

class SceneGenerator:
    def __init__(self):
        self.minimax = get_minimax_client()
    
    async def generate_scene(self, prompt: str, category: str = "custom", width: int = 1920, height: int = 1080) -> Dict:
        """使用 AI 生成场景背景"""
        full_prompt = f"{prompt}, high quality background, professional lighting, 16:9 aspect ratio"
        
        try:
            response = await self.minimax.generate_image(prompt=full_prompt, style="photorealistic", width=width, height=height)
            scene_url = response.get("data", {}).get("image_url", "")
        except Exception:
            scene_url = ""  # 模拟
        
        return {
            "scene_url": scene_url,
            "prompt": prompt,
            "category": category
        }
    
    async def save_generated_scene(self, db: Session, user_id: int, prompt: str, scene_url: str, name: str = None) -> Scene:
        """保存生成的场景"""
        scene = Scene(
            name=name or f"Custom: {prompt[:20]}...",
            category="custom",
            thumbnail_url=scene_url,
            scene_url=scene_url,
            is_active=True
        )
        db.add(scene)
        db.commit()
        db.refresh(scene)
        return scene
    
    def get_scene_presets(self) -> Dict:
        """获取场景预设提示词"""
        return {
            "business": ["Modern office with large windows", "Professional meeting room", "Corporate lobby"],
            "media": ["Professional TV studio with cameras", "News broadcasting room", "Podcast recording studio"],
            "education": ["Modern classroom with smart board", "University lecture hall", "Library reading room"],
            "outdoor": ["City skyline at sunset", "Park with trees and green grass", "Beach with ocean view"],
            "tech": ["Futuristic tech lab", "Data center with servers", "Cybersecurity operations room"]
        }
