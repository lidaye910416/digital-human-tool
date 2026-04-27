import os
from typing import Dict
from PIL import Image
from src.config import UPLOADS_DIR

class PhotoService:
    def __init__(self):
        self.allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
        self.max_size = 10 * 1024 * 1024  # 10MB
    
    def validate_photo(self, filename: str) -> Dict:
        """验证照片格式"""
        ext = os.path.splitext(filename)[1].lower()
        if ext not in self.allowed_extensions:
            return {"valid": False, "error": "Unsupported format"}
        return {"valid": True, "extension": ext}
    
    def process_photo(self, input_path: str, output_path: str, size: tuple = (512, 512), quality: int = 90) -> Dict:
        """处理照片：裁剪、缩放、压缩"""
        try:
            with Image.open(input_path) as img:
                if img.mode == "RGBA":
                    img = img.convert("RGB")
                
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                img.save(output_path, quality=quality, optimize=True)
                
                return {
                    "processed": True,
                    "output_path": output_path,
                    "size": os.path.getsize(output_path)
                }
        except Exception as e:
            return {"processed": False, "error": str(e)}
    
    def save_upload(self, file_content: bytes, filename: str, user_id: int) -> str:
        """保存上传的照片"""
        filepath = UPLOADS_DIR / f"{user_id}_{filename}"
        with open(filepath, 'wb') as f:
            f.write(file_content)
        return str(filepath)
