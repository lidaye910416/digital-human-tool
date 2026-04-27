import pytest
from src.services.preview_service import PreviewService

def test_processing_time_estimate():
    service = PreviewService()
    time1 = service.get_processing_time_estimate("a" * 60)
    assert time1 >= 60
    time2 = service.get_processing_time_estimate("short")
    assert time2 >= 30
