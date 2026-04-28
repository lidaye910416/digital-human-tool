#!/usr/bin/env python3
"""
TechEcho Pro - TTS Server
使用 MiniMax API 实现文字转语音，支持4种语音风格
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import hashlib
import requests
import tempfile
from pathlib import Path

app = Flask(__name__)
CORS(app)

# 配置
DATA_DIR = Path(__file__).parent.parent / "data"
AUDIO_DIR = DATA_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# MiniMax API 配置
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimax.chat/v1"

# 4种语音风格配置
VOICE_STYLES = {
    "voice1": {  # 磁性男声
        "voice_id": "male-qn-qingse",
        "name": "磁性男声",
        "description": "低沉稳重"
    },
    "voice2": {  # 活力男声
        "voice_id": "male-tx-jingxin",
        "name": "活力男声",
        "description": "年轻活力"
    },
    "voice3": {  # 温柔女声
        "voice_id": "female-shaonian",
        "name": "温柔女声",
        "description": "柔和亲切"
    },
    "voice4": {  # 知性女声
        "voice_id": "female-yanyu",
        "name": "知性女声",
        "description": "专业干练"
    }
}

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    """将文本转换为语音"""
    data = request.get_json()
    text = data.get('text', '')
    lang = data.get('lang', 'zh')
    voice = data.get('voice', 'voice1')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    if not MINIMAX_API_KEY:
        return jsonify({'error': 'MINIMAX_API_KEY not configured'}), 500
    
    # 生成缓存键
    cache_key = hashlib.md5((text[:200] + lang + voice).encode()).hexdigest()
    audio_file = AUDIO_DIR / f"{cache_key}.mp3"
    
    # 检查缓存
    if audio_file.exists():
        return jsonify({'audio_url': f'/data/audio/{cache_key}.mp3', 'cached': True})
    
    try:
        # 调用 MiniMax TTS API
        voice_id = VOICE_STYLES.get(voice, VOICE_STYLES["voice1"])["voice_id"]
        
        # 截取前500字符
        text = text[:500]
        
        # MiniMax TTS API
        url = f"{MINIMAX_BASE_URL}/t2a_v2"
        headers = {
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "speech-2.8-hd",
            "text": text,
            "stream": False,
            "voice_setting": {
                "voice_id": voice_id,
                "speed": 1.0,
                "volume": 1.0,
                "pitch": 0,
                "emotion": "neutral"
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("data") and result["data"].get("audio_file"):
                # 下载音频文件
                audio_url = result["data"]["audio_file"]
                audio_response = requests.get(audio_url, timeout=30)
                if audio_response.status_code == 200:
                    with open(audio_file, 'wb') as f:
                        f.write(audio_response.content)
                    return jsonify({
                        'audio_url': f'/data/audio/{cache_key}.mp3',
                        'cached': False,
                        'voice': voice,
                        'voice_name': VOICE_STYLES[voice]["name"]
                    })
        
        return jsonify({'error': 'TTS generation failed'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tts/voices', methods=['GET'])
def get_voices():
    """获取可用语音列表"""
    return jsonify({
        'voices': [
            {
                'id': vid,
                'name': vconf['name'],
                'description': vconf['description']
            }
            for vid, vconf in VOICE_STYLES.items()
        ]
    })

@app.route('/api/tts/generate-batch', methods=['POST'])
def generate_batch_tts():
    """批量生成语音（用于新闻收集后）"""
    data = request.get_json()
    news_items = data.get('news', [])
    lang = data.get('lang', 'zh')
    
    results = []
    for item in news_items:
        news_id = item.get('id')
        text = item.get('text', '')
        
        if not news_id or not text:
            continue
        
        for voice_id in VOICE_STYLES.keys():
            # 为每条新闻生成4种语音
            cache_key = hashlib.md5((news_id + voice_id).encode()).hexdigest()
            audio_file = AUDIO_DIR / f"{cache_key}.mp3"
            
            if not audio_file.exists():
                try:
                    # 调用 MiniMax TTS API
                    url = f"{MINIMAX_BASE_URL}/t2a_v2"
                    headers = {
                        "Authorization": f"Bearer {MINIMAX_API_KEY}",
                        "Content-Type": "application/json"
                    }
                    voice_config = VOICE_STYLES[voice_id]
                    payload = {
                        "model": "speech-2.8-hd",
                        "text": text[:500],
                        "stream": False,
                        "voice_setting": {
                            "voice_id": voice_config["voice_id"],
                            "speed": 1.0,
                            "volume": 1.0,
                            "pitch": 0,
                            "emotion": "neutral"
                        }
                    }
                    
                    response = requests.post(url, headers=headers, json=payload, timeout=30)
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("data") and result["data"].get("audio_file"):
                            audio_url = result["data"]["audio_file"]
                            audio_response = requests.get(audio_url, timeout=30)
                            if audio_response.status_code == 200:
                                with open(audio_file, 'wb') as f:
                                    f.write(audio_response.content)
                except Exception as e:
                    print(f"Error generating TTS for {news_id}/{voice_id}: {e}")
                    continue
            
            results.append({
                'news_id': news_id,
                'voice_id': voice_id,
                'audio_url': f'/data/audio/{cache_key}.mp3'
            })
    
    return jsonify({
        'generated': len(results),
        'files': results
    })

if __name__ == '__main__':
    print("TTS Server starting...")
    print(f"Audio directory: {AUDIO_DIR}")
    print(f"MiniMax API Key configured: {'Yes' if MINIMAX_API_KEY else 'No'}")
    print("Available voices:")
    for vid, vconf in VOICE_STYLES.items():
        print(f"  - {vid}: {vconf['name']} ({vconf['description']})")
    print("\nEndpoints:")
    print("  POST /api/tts - Generate TTS for single text")
    print("  GET /api/tts/voices - List available voices")
    print("  POST /api/tts/generate-batch - Batch generate TTS for news")
    app.run(host='0.0.0.0', port=5001, debug=True)
