import pytest
from src.services.photo_service import PhotoService

def test_validate_photo():
    service = PhotoService()
    result = service.validate_photo("test.jpg")
    assert result["valid"] == True
    assert result["extension"] == ".jpg"

def test_validate_photo_invalid():
    service = PhotoService()
    result = service.validate_photo("test.gif")
    assert result["valid"] == False
