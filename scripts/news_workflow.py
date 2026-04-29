#!/usr/bin/env python3
"""
TechEcho Pro - 新闻收集与TTS生成工作流

完整流程:
1. 收集新闻
2. AI质量校准（MiniMax 2.7）
3. 分类验证与修正
4. 过滤无关内容
5. 生成四种语音
6. 保存到数据库/文件

AI校准策略:
- MiniMax API: 校准分数、验证分类、过滤无关内容
- 四大分类: AI, tools, news, product
- 舍弃: 游戏、娱乐等无关内容

TTS策略:
- MiniMax API: 高质量语音，配额有限
- edge-tts: 兜底方案，免费无限制

用法:
    python scripts/news_workflow.py              # 完整流程
    python scripts/news_workflow.py --skip-tts  # 跳过TTS生成
    python scripts/news_workflow.py --skip-ai   # 跳过AI校准
"""

import argparse
import asyncio
import json
import os
import sys
import hashlib
import requests
from datetime import datetime
from pathlib import Path

import edge_tts

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# MiniMax API 配置
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimax.chat/v1"
MINIMAX_DAILY_LIMIT = 11000  # 免费用户每日限制

# 4种语音风格 - 统一voice_id供MiniMax使用
VOICE_STYLES = {
    "voice1": {
        "name": "晓晓-女声",
        "minimax": "female-tianmei",   # MiniMax voice ID
        "edge": "zh-CN-XiaoxiaoNeural"  # edge-tts voice
    },
    "voice2": {
        "name": "云希-男声",
        "minimax": "male-qn-qingse",
        "edge": "zh-CN-YunxiNeural"
    },
    "voice3": {
        "name": "晓伊-女声",
        "minimax": "female-yizhi",
        "edge": "zh-CN-XiaoyiNeural"
    },
    "voice4": {
        "name": "云扬-男声",
        "minimax": "male-tx-jingxin",
        "edge": "zh-CN-YunyangNeural"
    }
}

async def collect_news(category=None, lang=None, limit=None, min_quality=55):
    """收集新闻"""
    print("\n[1/4] 收集新闻...")
    
    try:
        from services.news_collector_v2 import BilingualNewsCollector
        collector = BilingualNewsCollector()
        news_items = await collector.collect_all(lang=lang, category=category)
        
        # 过滤低质量
        filtered = [n for n in news_items if (n.quality.total_100 if n.quality else 0) >= min_quality]
        filtered.sort(key=lambda x: x.quality.total_100 if x.quality else 0, reverse=True)
        
        if limit:
            filtered = filtered[:limit]
        
        print(f"   收集到 {len(filtered)} 条高质量新闻")
        return filtered
    except Exception as e:
        print(f"   收集失败: {e}")
        return []

def convert_to_dict(item):
    """转换为字典"""
    return {
        'id': item.id,
        'title_zh': item.title_zh,
        'title_en': item.title_en,
        'summary_zh': item.summary_zh,
        'summary_en': item.summary_en,
        'content_zh': item.content_zh,
        'content_en': item.content_en,
        'source_zh': item.source_zh,
        'source_en': item.source_en,
        'source_url': item.source_url,
        'lang': item.lang,
        'category': item.category,
        'published_at': item.published_at,
        'created_at': item.created_at,
        'quality': {
            'total_100': item.quality.total_100 if item.quality else 0,
            'grade': item.quality.grade if item.quality else 'D',
            'scores': item.quality.scores if item.quality else {}
        }
    }

def get_text_for_tts(news_dict):
    """获取要转换的文本"""
    lang = news_dict['lang']
    if lang == 'zh':
        return news_dict.get('content_zh') or news_dict.get('summary_zh') or news_dict.get('title_zh', '')
    else:
        return news_dict.get('content_en') or news_dict.get('summary_en') or news_dict.get('title_en', '')

async def generate_tts_minimax(news_id, text, voice_id, audio_file):
    """使用MiniMax API生成语音"""
    if not MINIMAX_API_KEY:
        return False, "API密钥未配置"

    try:
        url = f"{MINIMAX_BASE_URL}/t2a_v2"
        headers = {
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "speech-2.8-hd",
            "text": text[:500],
            "stream": False,
            "voice_setting": {
                "voice_id": VOICE_STYLES[voice_id]["minimax"],
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
                    return True, "MiniMax成功"
        elif response.status_code == 400:
            error = response.json()
            if "quota" in str(error).lower() or "limit" in str(error).lower():
                return False, "配额用尽"
            return False, str(error)
        else:
            return False, f"HTTP {response.status_code}"

    except Exception as e:
        return False, str(e)

    return False, "未知错误"

async def generate_tts_edge(news_id, text, voice_id, audio_file):
    """使用edge-tts生成语音（兜底方案）"""
    try:
        communicate = edge_tts.Communicate(text[:500], VOICE_STYLES[voice_id]["edge"])
        await communicate.save(str(audio_file))
        return True, "edge-tts成功"
    except Exception as e:
        return False, str(e)

async def generate_tts_for_news(news_dict, audio_dir, minimax_available=True):
    """为单条新闻生成4种语音

    策略:
    1. 高质量新闻: 优先MiniMax
    2. MiniMax失败/配额用尽: 切换edge-tts
    """
    news_id = news_dict['id']
    text = get_text_for_tts(news_dict)

    if not text:
        return []

    results = []
    minimax_failed = False

    for voice_id, voice_conf in VOICE_STYLES.items():
        cache_key = hashlib.md5((news_id + voice_id).encode()).hexdigest()
        audio_file = audio_dir / f"{cache_key}.mp3"

        # 已缓存则跳过
        if audio_file.exists():
            results.append({
                'news_id': news_id,
                'voice_id': voice_id,
                'audio_url': f'/data/audio/{cache_key}.mp3',
                'cached': True,
                'engine': 'cached'
            })
            continue

        success = False
        engine = 'unknown'

        # 优先MiniMax（如果没有失败过）
        if minimax_available and not minimax_failed:
            success, msg = await generate_tts_minimax(news_id, text, voice_id, audio_file)
            if success:
                engine = 'minimax'
                print(f"      ✅ {voice_conf['name']} [MiniMax]")

        # MiniMax失败则用edge-tts兜底
        if not success:
            success, msg = await generate_tts_edge(news_id, text, voice_id, audio_file)
            if success:
                engine = 'edge-tts'
                print(f"      ✅ {voice_conf['name']} [edge-tts]")
            else:
                print(f"      ❌ {voice_conf['name']} 失败: {msg}")
                # 标记MiniMax不可用
                if "配额" in msg or "quota" in msg.lower():
                    minimax_failed = True

        if success:
            results.append({
                'news_id': news_id,
                'voice_id': voice_id,
                'audio_url': f'/data/audio/{cache_key}.mp3',
                'cached': False,
                'engine': engine
            })

    return results

def generate_tts(news_dict, audio_dir, minimax_available=True):
    """为单条新闻生成4种语音"""
    return asyncio.run(generate_tts_for_news(news_dict, audio_dir, minimax_available))


def run_ai_calibration(news_list, skip_ai=False):
    """运行AI质量校准

    流程:
    1. 使用MiniMax 2.7模型校准分数
    2. 验证分类(AI/tools/news/product)
    3. 过滤无关内容(游戏/娱乐等)
    4. 修正不合理的分数
    """
    from services.news_ai_calibrator import NewsAICalibrator

    if skip_ai or not MINIMAX_API_KEY:
        print(f"\n[2/6] 跳过AI校准")
        return news_list, {"total": len(news_list), "passed": len(news_list),
                          "ai_calibration": "disabled"}

    calibrator = NewsAICalibrator(MINIMAX_API_KEY)
    calibrated, stats = calibrator.batch_calibrate(news_list)

    return calibrated, stats


def run_workflow(skip_tts=False, skip_ai=False, min_quality=55):
    """运行完整工作流"""
    print("=" * 50)
    print("TechEcho Pro - 新闻收集与TTS工作流")
    print("=" * 50)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"最低质量阈值: {min_quality}")
    print(f"跳过TTS: {'是' if skip_tts else '否'}")
    print(f"跳过AI校准: {'是' if skip_ai else '否'}")
    print(f"MiniMax API: {'已配置' if MINIMAX_API_KEY else '未配置'}")
    print("-" * 50)

    # 创建目录
    audio_dir = Path(__file__).parent.parent / "data" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    # [1/6] 收集新闻
    print(f"\n[1/6] 收集新闻...")
    news_items = asyncio.run(collect_news(min_quality=min_quality))

    if not news_items:
        print("\n❌ 没有收集到新闻")
        return

    # 转换为字典（已按分数排序）
    news_list = [convert_to_dict(n) for n in news_items]
    print(f"   收集到 {len(news_list)} 条新闻")

    # [2/6] AI校准
    calibrated_news, calibration_stats = run_ai_calibration(news_list, skip_ai)

    # 按校准后分数重新排序
    calibrated_news.sort(key=lambda x: x['quality']['total_100'], reverse=True)

    # [3/6] 过滤极低分（校准后低于50分）
    print(f"\n[3/6] 质量过滤...")
    filtered_news = [n for n in calibrated_news if n['quality']['total_100'] >= min_quality]
    print(f"   过滤后: {len(filtered_news)} 条")

    # 生成TTS
    tts_results = []
    minimax_failed = False
    tts_stats = {'minimax': 0, 'edge_tts': 0, 'cached': 0}

    if not skip_tts:
        print(f"\n[4/6] 生成语音 (4种风格)...")
        for i, news in enumerate(filtered_news):
            print(f"   [{i+1}/{len(filtered_news)}] {news['title_zh'][:30]}...")
            results = generate_tts(news, audio_dir, minimax_available=(not minimax_failed))
            tts_results.extend(results)

            # 统计
            for r in results:
                if r.get('cached'):
                    tts_stats['cached'] += 1
                elif r.get('engine') == 'minimax':
                    tts_stats['minimax'] += 1
                elif r.get('engine') == 'edge-tts':
                    tts_stats['edge_tts'] += 1

            # 如果MiniMax配额用尽，后续全部用edge-tts
            if 'minimax' in [r.get('engine') for r in results]:
                continue
            if not minimax_failed:
                minimax_failed = True
                print(f"   ⚠️ MiniMax配额用尽，后续使用edge-tts")

        print(f"\n   📊 TTS统计:")
        print(f"      MiniMax: {tts_stats['minimax']} 个")
        print(f"      edge-tts: {tts_stats['edge_tts']} 个")
        print(f"      缓存: {tts_stats['cached']} 个")
        print(f"      总计: {len(tts_results)} 个")
    else:
        print("\n[4/6] 跳过TTS生成")

    # 添加语音URL到新闻
    tts_map = {}
    for t in tts_results:
        news_id = t['news_id']
        if news_id not in tts_map:
            tts_map[news_id] = {}
        tts_map[news_id][t['voice_id']] = t['audio_url']

    for news in filtered_news:
        news['audio'] = tts_map.get(news['id'], {})

    # [5/6] 保存
    print(f"\n[5/6] 保存新闻数据...")

    # 分类统计
    category_stats = {'ai': 0, 'tools': 0, 'news': 0, 'product': 0}
    for n in filtered_news:
        cat = n.get('category', 'news')
        if cat in category_stats:
            category_stats[cat] += 1

    output_data = {
        'lastUpdate': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'totalCount': len(filtered_news),
        'stats': {
            'A+': len([n for n in filtered_news if n['quality']['grade'] == 'A+']),
            'A': len([n for n in filtered_news if n['quality']['grade'] == 'A']),
            'B': len([n for n in filtered_news if n['quality']['grade'] == 'B']),
            'C': len([n for n in filtered_news if n['quality']['grade'] == 'C']),
            'D': len([n for n in filtered_news if n['quality']['grade'] == 'D'])
        },
        'categories': category_stats,
        'news': filtered_news
    }

    output_path = Path(__file__).parent.parent / "app" / "data" / "news.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"   保存到: {output_path}")

    # [6/6] 完成
    print("\n[6/6] 完成!")
    print("-" * 50)
    print(f"✅ 总计: {len(filtered_news)} 条新闻")
    print(f"   分类: AI({category_stats['ai']}) 工具({category_stats['tools']}) 动态({category_stats['news']}) 产品({category_stats['product']})")
    print(f"✅ 语音: {len(tts_results)} 个文件")
    if not skip_tts:
        print(f"   (MiniMax: {tts_stats['minimax']}, edge-tts: {tts_stats['edge_tts']}, 缓存: {tts_stats['cached']})")
    if not skip_ai and MINIMAX_API_KEY:
        print(f"✅ AI校准: 通过{calibration_stats.get('passed', 0)}, 修正{calibration_stats.get('adjusted', 0)}, 舍弃{calibration_stats.get('discarded', 0)}")
    
    # 添加语音URL到新闻
    tts_map = {}
    for t in tts_results:
        news_id = t['news_id']
        if news_id not in tts_map:
            tts_map[news_id] = {}
        tts_map[news_id][t['voice_id']] = t['audio_url']
    
    for news in news_list:
        news['audio'] = tts_map.get(news['id'], {})
    
    # 保存
    print(f"\n[3/4] 保存新闻数据...")
    output_data = {
        'lastUpdate': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'totalCount': len(news_list),
        'stats': {
            'A+': len([n for n in news_list if n['quality']['grade'] == 'A+']),
            'A': len([n for n in news_list if n['quality']['grade'] == 'A']),
            'B': len([n for n in news_list if n['quality']['grade'] == 'B']),
            'C': len([n for n in news_list if n['quality']['grade'] == 'C']),
            'D': len([n for n in news_list if n['quality']['grade'] == 'D'])
        },
        'categories': list(set(n['category'] for n in news_list)),
        'news': news_list
    }
    
    output_path = Path(__file__).parent.parent / "app" / "data" / "news.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"   保存到: {output_path}")
    
    print("\n[4/4] 完成!")
    print("-" * 50)
    print(f"✅ 总计: {len(news_list)} 条新闻")
    print(f"✅ 语音: {len(tts_results)} 个文件")
    if not skip_tts:
        print(f"   (MiniMax: {tts_stats['minimax']}, edge-tts: {tts_stats['edge_tts']}, 缓存: {tts_stats['cached']})")

def main():
    parser = argparse.ArgumentParser(description='TechEcho Pro 新闻收集与TTS工作流')
    parser.add_argument('--skip-tts', action='store_true', help='跳过TTS生成')
    parser.add_argument('--skip-ai', action='store_true', help='跳过AI校准')
    parser.add_argument('--min-quality', type=int, default=55, help='最低质量分数 (默认55)')

    args = parser.parse_args()

    run_workflow(
        skip_tts=args.skip_tts,
        skip_ai=args.skip_ai,
        min_quality=args.min_quality
    )

if __name__ == '__main__':
    main()
