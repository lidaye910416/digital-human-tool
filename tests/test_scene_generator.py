import pytest
from src.services.scene_generator import SceneGenerator

def test_get_scene_presets():
    generator = SceneGenerator()
    presets = generator.get_scene_presets()
    assert "business" in presets
    assert "media" in presets
    assert len(presets["business"]) == 3
