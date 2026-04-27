from typing import Dict, List

class LanguageService:
    def __init__(self):
        self.supported_languages = [
            {"code": "zh-CN", "name": "中文（简体）", "native": "简体中文"},
            {"code": "zh-TW", "name": "中文（繁体）", "native": "繁體中文"},
            {"code": "en-US", "name": "English", "native": "English"},
            {"code": "ja-JP", "name": "Japanese", "native": "日本語"},
            {"code": "ko-KR", "name": "Korean", "native": "한국어"},
        ]
    
    def get_languages(self) -> List[Dict]:
        return self.supported_languages
    
    def get_voices_for_language(self, language_code: str) -> List[Dict]:
        if language_code == "zh-CN":
            return [
                {"id": "zh-female-1", "name": "中文女声1", "gender": "female"},
                {"id": "zh-male-1", "name": "中文男声1", "gender": "male"},
            ]
        elif language_code == "en-US":
            return [
                {"id": "en-female-1", "name": "English Female", "gender": "female"},
                {"id": "en-male-1", "name": "English Male", "gender": "male"},
            ]
        return []
    
    def detect_language(self, text: str) -> str:
        for char in text:
            if '一' <= char <= '鿿':
                return "zh-CN"
        return "en-US"
