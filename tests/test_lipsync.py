import pytest
from src.services.lipsync_service import LipSyncService

def test_calculate_credits():
    service = LipSyncService()
    credits = service.calculate_credits(30)
    assert credits == 15  # 30 * 0.5 = 15
