import pytest

def test_calculate_credits():
    from src.services.video_service import VideoService
    service = VideoService()
    credits = service.calculate_credits("短文本")
    assert credits >= 10  # 最小值
