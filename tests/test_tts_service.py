import pytest

def test_calculate_credits():
    from src.services.tts_service import TextToSpeechService
    service = TextToSpeechService()
    credits = service.calculate_credits("这是一个测试文本，长度为六十个字符。" * 10)
    assert credits >= 1

def test_get_available_voices():
    from src.services.tts_service import TextToSpeechService
    service = TextToSpeechService()
    voices = service.get_available_voices()
    assert len(voices) > 0
