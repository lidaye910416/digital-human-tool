import pytest
from src.services.export_service import ExportService

def test_export_mp4():
    service = ExportService()
    result = service.export_as_mp4("http://example.com/video.mp4", "1080p")
    assert result["format"] == "mp4"
    assert result["quality"] == "1080p"

def test_export_gif():
    service = ExportService()
    result = service.export_as_gif("http://example.com/video.mp4", fps=10)
    assert result["format"] == "gif"
    assert result["fps"] == 10

def test_generate_share_link():
    service = ExportService()
    link = service.generate_share_link("http://example.com/video.mp4", "twitter")
    assert "twitter.com" in link or "x.com" in link
