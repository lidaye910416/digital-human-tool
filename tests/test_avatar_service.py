import pytest

def test_calculate_avatar_credits():
    from src.services.avatar_service import AvatarService
    service = AvatarService()
    
    ai_credits = service.calculate_avatar_credits("ai_generated")
    assert ai_credits == 5
    
    photo_credits = service.calculate_avatar_credits("photo_driven")
    assert photo_credits == 3
