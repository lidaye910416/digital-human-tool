from typing import Dict, Any
from src.services.minimax_client import get_minimax_client
from src.services.azure_tts_client import get_azure_tts_client
import os

class TextToSpeechService:
    def __init__(self):
        self.minimax = get_minimax_client()
        self.azure = get_azure_tts_client()

        # MiniMax 系统 Voice ID (来自 MiniMax 官方文档)
        self.minimax_voices = [
            "female-tianmei", "female-shaonv", "female-yujie", "female-chengshu",
            "male-tianmei", "male-shaonv", "male-yujie", "male-qn", "male-chengshu"
        ]

        # 确定使用的 TTS 提供商
        self.provider = self._detect_provider()

    def _detect_provider(self) -> str:
        """检测可用的 TTS 提供商"""
        # 优先使用 Azure TTS
        if os.environ.get("AZURE_SPEECH_KEY") or os.environ.get("AZURE_TTS_KEY"):
            return "azure"

        # 检查 MiniMax 是否可用
        # 目前默认 mock，因为 MiniMax Token Plan 问题
        return "mock"

    async def synthesize(self, text: str, voice_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """将文字转换为语音"""
        config = voice_config or {"voice_id": "female-tianmei", "speed": 1.0}
        voice_id = config.get("voice_id", "female-tianmei")

        if self.provider == "azure":
            # 使用 Azure TTS
            result = await self.azure.synthesize(
                text=text,
                voice_id=voice_id,
                speed=config.get("speed", 1.0)
            )
            return {
                "audio_url": result.get("data", {}).get("audio_url", ""),
                "text_length": len(text),
                "voice_id": voice_id,
                "provider": "azure"
            }
        elif self.provider == "minimax":
            # 使用 MiniMax TTS
            if voice_id not in self.minimax_voices:
                voice_id = "female-tianmei"

            response = await self.minimax.text_to_speech(
                text=text,
                voice_id=voice_id
            )
            return {
                "audio_url": response.get("data", {}).get("audio_url", ""),
                "text_length": len(text),
                "voice_id": voice_id,
                "provider": "minimax"
            }
        else:
            # Mock 模式
            return {
                "audio_url": "data:audio/mp3;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=",
                "text_length": len(text),
                "voice_id": voice_id,
                "provider": "mock"
            }

    def calculate_credits(self, text: str) -> int:
        return max(1, len(text) // 60)

    def get_available_voices(self) -> list:
        """返回所有可用的声音"""
        voices = []

        # MiniMax 声音 (官方系统声音)
        minimax_voice_names = {
            "female-tianmei": "甜美女声",
            "female-shaonv": "少 女声",
            "female-yujie": "御姐女声",
            "female-chengshu": "成熟女声",
            "male-tianmei": "甜 美男声",
            "male-shaonv": "少 年男声",
            "male-yujie": "御姐男声",
            "male-qn": "青年男声",
            "male-chengshu": "成熟男声",
        }
        for v in self.minimax_voices:
            voices.append({
                "id": v,
                "name": minimax_voice_names.get(v, v),
                "gender": "female" if "female" in v else "male",
                "provider": "minimax"
            })

        # Azure 声音
        for v in self.azure.get_available_voices():
            voices.append({
                "id": v["id"],
                "name": v["name"],
                "gender": "female" if "Neural" in v["id"] and "Guy" not in v["id"] else "male",
                "language": v["language"],
                "provider": "azure"
            })

        return voices
