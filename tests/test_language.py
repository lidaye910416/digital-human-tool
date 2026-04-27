import pytest
from src.services.language_service import LanguageService

def test_get_languages():
    service = LanguageService()
    languages = service.get_languages()
    assert len(languages) >= 4
    assert any(lang["code"] == "zh-CN" for lang in languages)

def test_detect_language():
    service = LanguageService()
    assert service.detect_language("你好世界") == "zh-CN"
    assert service.detect_language("Hello World") == "en-US"
