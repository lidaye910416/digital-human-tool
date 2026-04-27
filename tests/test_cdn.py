import pytest
from src.utils.cdn import CDNManager

def test_get_url():
    manager = CDNManager()
    assert manager.get_url("test.jpg") == "/static/test.jpg"

def test_get_video_url():
    manager = CDNManager()
    assert "videos/" in manager.get_video_url("123")
