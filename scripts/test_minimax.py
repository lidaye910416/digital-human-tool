#!/usr/bin/env python3
"""Test MiniMax TTS API"""
import os
import requests

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimax.chat/v1"

test_text = "你好，这是测试语音。"

payload = {
    "model": "speech-2.8-hd",
    "text": test_text,
    "stream": False,
    "voice_setting": {
        "voice_id": "male-qn-qingse",
        "speed": 1.0,
        "volume": 1.0,
        "pitch": 0,
        "emotion": "neutral"
    }
}

headers = {
    "Authorization": f"Bearer {MINIMAX_API_KEY}",
    "Content-Type": "application/json"
}

print("Testing MiniMax TTS API...")
print(f"URL: {MINIMAX_BASE_URL}/t2a_v2")
print(f"Text: {test_text}")

try:
    response = requests.post(
        f"{MINIMAX_BASE_URL}/t2a_v2",
        headers=headers,
        json=payload,
        timeout=30
    )
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
