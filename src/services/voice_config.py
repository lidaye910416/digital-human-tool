"""
统一语音配置服务

整合所有 TTS 提供商的语音配置
"""

from typing import Dict, List, Optional, Callable


# ===== 语音风格定义 (工作流使用的 4 种声音) =====

VOICE_STYLES: Dict[str, Dict] = {
    "voice1": {
        "name": "晓晓-女声",
        "minimax": "female-tianmei",
        "edge": "zh-CN-XiaoxiaoNeural",
        "azure": "zh-CN-XiaoxiaoNeural",
        "gender": "female",
    },
    "voice2": {
        "name": "云希-男声",
        "minimax": "male-qn-qingse",
        "edge": "zh-CN-YunxiNeural",
        "azure": "zh-CN-YunxiNeural",
        "gender": "male",
    },
    "voice3": {
        "name": "晓伊-女声",
        "minimax": "female-yizhi",
        "edge": "zh-CN-XiaoyiNeural",
        "azure": "zh-CN-XiaoyiNeural",
        "gender": "female",
    },
    "voice4": {
        "name": "云扬-男声",
        "minimax": "male-tx-jingxin",
        "edge": "zh-CN-YunyangNeural",
        "azure": "zh-CN-YunyangNeural",
        "gender": "male",
    },
}


# ===== MiniMax 系统语音 =====

MINIMAX_VOICES: List[Dict] = [
    {"id": "female-tianmei", "name": "甜美女声", "gender": "female", "age": "young", "available": True},
    {"id": "female-shaonv", "name": "少女声", "gender": "female", "age": "young", "available": True},
    {"id": "female-yujie", "name": "御姐女声", "gender": "female", "age": "adult", "available": True},
    {"id": "female-chengshu", "name": "成熟女声", "gender": "female", "age": "middle", "available": True},
    {"id": "male-tianmei", "name": "甜美男声", "gender": "male", "age": "young", "available": False},
    {"id": "male-shaonv", "name": "少年男声", "gender": "male", "age": "young", "available": False},
    {"id": "male-yujie", "name": "御姐男声", "gender": "male", "age": "adult", "available": False},
    {"id": "male-qn", "name": "青年男声", "gender": "male", "age": "young", "available": False},
    {"id": "male-chengshu", "name": "成熟男声", "gender": "male", "age": "middle", "available": False},
]


# ===== edge-tts / Azure 语音 =====

EDGE_VOICES: List[Dict] = [
    {"id": "zh-CN-XiaoxiaoNeural", "name": "晓晓 (女声)", "language": "zh-CN", "gender": "female"},
    {"id": "zh-CN-YunxiNeural", "name": "云希 (男声)", "language": "zh-CN", "gender": "male"},
    {"id": "zh-CN-XiaoyiNeural", "name": "晓伊 (女声)", "language": "zh-CN", "gender": "female"},
    {"id": "zh-CN-YunyangNeural", "name": "云扬 (男声)", "language": "zh-CN", "gender": "male"},
    {"id": "en-US-JennyNeural", "name": "Jenny (女声)", "language": "en-US", "gender": "female"},
    {"id": "en-US-GuyNeural", "name": "Guy (男声)", "language": "en-US", "gender": "male"},
]


class VoiceConfigService:
    """语音配置服务"""

    def __init__(self):
        self.voices = MINIMAX_VOICES

    def get_all_voices(self) -> List[Dict]:
        return self.voices

    def get_available_voices(self) -> List[Dict]:
        """只返回可用的声音"""
        return [v for v in self.voices if v.get("available", True)]

    def get_voices_by_gender(self, gender: str) -> List[Dict]:
        return [v for v in self.voices if v["gender"] == gender]

    def get_voice_style(self, voice_id: str) -> Optional[Dict]:
        """获取指定语音风格的配置"""
        return VOICE_STYLES.get(voice_id)

    def get_all_voice_styles(self) -> List[str]:
        """返回所有可用的语音风格 ID"""
        return list(VOICE_STYLES.keys())

    def get_emotion_styles(self) -> List[str]:
        return ["professional", "warm", "energetic", "calm", "friendly"]

    def apply_preset(self, preset_name: str) -> Dict:
        presets = {
            "professional_female": {"voice_id": "female-tianmei", "speed": 1.0, "emotion": "professional"},
            "professional_male": {"voice_id": "female-tianmei", "speed": 1.0, "emotion": "professional"},
            "friendly_female": {"voice_id": "female-shaonv", "speed": 1.1, "emotion": "friendly"},
            "friendly_male": {"voice_id": "female-shaonv", "speed": 1.1, "emotion": "friendly"},
            "energetic_female": {"voice_id": "female-yujie", "speed": 1.2, "emotion": "energetic"},
            "calm_male": {"voice_id": "female-chengshu", "speed": 0.9, "emotion": "calm"}
        }
        return presets.get(preset_name, presets["professional_female"])


# 全局实例
voice_config = VoiceConfigService()
