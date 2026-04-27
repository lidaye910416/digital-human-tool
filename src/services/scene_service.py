from typing import List, Optional
from sqlalchemy.orm import Session
from src.models.scene import Scene

class SceneService:
    def get_all_scenes(self, db: Session) -> List[dict]:
        scenes = db.query(Scene).filter(Scene.is_active == True).all()
        return [self._scene_to_dict(s) for s in scenes]
    
    def get_scenes_by_category(self, db: Session, category: str) -> List[dict]:
        scenes = db.query(Scene).filter(Scene.category == category, Scene.is_active == True).all()
        return [self._scene_to_dict(s) for s in scenes]
    
    def get_scene_by_id(self, db: Session, scene_id: int) -> Optional[dict]:
        scene = db.query(Scene).filter(Scene.id == scene_id).first()
        return self._scene_to_dict(scene) if scene else None
    
    def create_scene(self, db: Session, name: str, category: str, thumbnail_url: str = "", scene_url: str = "") -> Scene:
        scene = Scene(name=name, category=category, thumbnail_url=thumbnail_url, scene_url=scene_url, is_active=True)
        db.add(scene)
        db.commit()
        db.refresh(scene)
        return scene
    
    def _scene_to_dict(self, scene: Scene) -> dict:
        return {
            "id": scene.id,
            "name": scene.name,
            "category": scene.category,
            "thumbnail_url": scene.thumbnail_url,
            "scene_url": scene.scene_url
        }
    
    def init_default_scenes(self, db: Session):
        default_scenes = [
            {"name": "现代办公室", "category": "business"},
            {"name": "会议室", "category": "business"},
            {"name": "专业演播室", "category": "media"},
            {"name": "新闻直播间", "category": "media"},
            {"name": "教室", "category": "education"},
            {"name": "户外自然", "category": "outdoor"},
            {"name": "科技感", "category": "tech"},
        ]
        
        for scene_data in default_scenes:
            existing = db.query(Scene).filter(Scene.name == scene_data["name"]).first()
            if not existing:
                self.create_scene(db, name=scene_data["name"], category=scene_data["category"])
