import pytest
from src.services.voice_config import VoiceConfigService

def test_get_all_voices():
    service = VoiceConfigService()
    voices = service.get_all_voices()
    assert len(voices) >= 4

def test_apply_preset():
    service = VoiceConfigService()
    config = service.apply_preset("professional_female")
    assert config["voice_id"] == "female-shukong"
    assert config["emotion"] == "professional"

def test_get_emotion_styles():
    service = VoiceConfigService()
    emotions = service.get_emotion_styles()
    assert "professional" in emotions
    assert "warm" in emotions
