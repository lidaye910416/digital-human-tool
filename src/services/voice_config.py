from typing import Dict, List

class VoiceConfigService:
    def __init__(self):
        # MiniMax 可用的声音列表
        # 女声：全部可用
        # 男声：需要开通权限，暂时不可用
        self.voices = [
            # 可用的女声
            {"id": "female-tianmei", "name": "甜美女声", "gender": "female", "age": "young", "available": True},
            {"id": "female-shaonv", "name": "少女声", "gender": "female", "age": "young", "available": True},
            {"id": "female-yujie", "name": "御姐女声", "gender": "female", "age": "adult", "available": True},
            {"id": "female-chengshu", "name": "成熟女声", "gender": "female", "age": "middle", "available": True},
            # 暂时不可用的男声（需要开通 MiniMax 语音权限）
            {"id": "male-tianmei", "name": "甜美男声", "gender": "male", "age": "young", "available": False},
            {"id": "male-shaonv", "name": "少年男声", "gender": "male", "age": "young", "available": False},
            {"id": "male-yujie", "name": "御姐男声", "gender": "male", "age": "adult", "available": False},
            {"id": "male-qn", "name": "青年男声", "gender": "male", "age": "young", "available": False},
            {"id": "male-chengshu", "name": "成熟男声", "gender": "male", "age": "middle", "available": False},
        ]

    def get_all_voices(self) -> List[Dict]:
        return self.voices
    
    def get_available_voices(self) -> List[Dict]:
        """只返回可用的声音"""
        return [v for v in self.voices if v.get("available", True)]

    def get_voices_by_gender(self, gender: str) -> List[Dict]:
        return [v for v in self.voices if v["gender"] == gender]

    def get_emotion_styles(self) -> List[str]:
        return ["professional", "warm", "energetic", "calm", "friendly"]

    def apply_preset(self, preset_name: str) -> Dict:
        presets = {
            "professional_female": {"voice_id": "female-tianmei", "speed": 1.0, "emotion": "professional"},
            "professional_male": {"voice_id": "female-tianmei", "speed": 1.0, "emotion": "professional"},  # 暂时用女声
            "friendly_female": {"voice_id": "female-shaonv", "speed": 1.1, "emotion": "friendly"},
            "friendly_male": {"voice_id": "female-shaonv", "speed": 1.1, "emotion": "friendly"},  # 暂时用女声
            "energetic_female": {"voice_id": "female-yujie", "speed": 1.2, "emotion": "energetic"},
            "calm_male": {"voice_id": "female-chengshu", "speed": 0.9, "emotion": "calm"}  # 暂时用女声
        }
        return presets.get(preset_name, presets["professional_female"])


# 测试声音是否可用
async def test_voice(voice_id: str) -> bool:
    """测试声音是否可用"""
    from src.services.minimax_client import get_minimax_client
    client = get_minimax_client()
    try:
        result = await client.text_to_speech("测试", voice_id)
        return bool(result.get("data", {}).get("audio_url"))
    except:
        return False
