import os
from typing import Optional

class CDNManager:
    def __init__(self):
        self.cdn_prefix = os.getenv("CDN_URL", "")
        self.local_prefix = "/static"
    
    def get_url(self, resource_path: str) -> str:
        if self.cdn_prefix:
            return f"{self.cdn_prefix}/{resource_path}"
        return f"{self.local_prefix}/{resource_path}"
    
    def get_video_url(self, video_id: str) -> str:
        return self.get_url(f"videos/{video_id}")
    
    def get_avatar_url(self, avatar_id: str) -> str:
        return self.get_url(f"avatars/{avatar_id}")
    
    def get_scene_url(self, scene_id: str) -> str:
        return self.get_url(f"scenes/{scene_id}")
