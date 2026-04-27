from typing import Dict
from src.config import VIDEOS_DIR

class ExportService:
    def __init__(self):
        self.ffmpeg_available = True  # 简化检查
    
    def export_as_mp4(self, video_url: str, quality: str = "1080p", output_filename: str = None) -> Dict:
        """导出为 MP4 格式"""
        if output_filename is None:
            output_filename = f"export_{quality}.mp4"
        output_path = VIDEOS_DIR / output_filename
        return {
            "format": "mp4",
            "quality": quality,
            "output_url": str(output_path),
            "download_url": video_url
        }
    
    def export_as_gif(self, video_url: str, fps: int = 10, start_time: float = 0, duration: float = 5, width: int = 480) -> Dict:
        """导出为 GIF 格式"""
        output_filename = f"export_gif_{fps}fps.gif"
        output_path = VIDEOS_DIR / output_filename
        return {
            "format": "gif",
            "fps": fps,
            "width": width,
            "output_url": str(output_path),
            "download_url": video_url
        }
    
    def generate_share_link(self, video_url: str, platform: str = "general") -> str:
        """生成分享链接"""
        share_links = {
            "twitter": f"https://twitter.com/intent/tweet?url={video_url}&text=Check%20this%20video",
            "facebook": f"https://www.facebook.com/sharer/sharer.php?u={video_url}",
            "linkedin": f"https://www.linkedin.com/shareArticle?mini=true&url={video_url}",
            "general": video_url
        }
        return share_links.get(platform, video_url)
