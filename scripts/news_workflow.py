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
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.services.tts_service import TTSService, get_tts_service
from src.services.voice_config import VOICE_STYLES

# MiniMax API 配置
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")


async def collect_news(category=None, lang=None, limit=None, min_quality=55):
    """收集新闻"""
    print("\n[1/6] 收集新闻...")

    try:
        from src.services.news_collector import NewsCollector

        async with NewsCollector(rss_enabled=True, web_enabled=False, api_enabled=False) as collector:
            news_items = await collector.collect(
                lang=lang,
                category=category,
                min_quality=0  # 先收集，后过滤
            )

        # 过滤低质量
        filtered = [n for n in news_items if (n.quality.total_100 if n.quality else 0) >= min_quality]

        if limit:
            filtered = filtered[:limit]

        print(f"   收集到 {len(filtered)} 条高质量新闻")
        return filtered
    except Exception as e:
        print(f"   收集失败: {e}")
        return []


def news_item_to_dict(item) -> Dict:
    """将 NewsItem 转换为字典"""
    if hasattr(item, 'to_dict'):
        return item.to_dict()
    return {
        'id': getattr(item, 'id', ''),
        'title_zh': getattr(item, 'title_zh', ''),
        'title_en': getattr(item, 'title_en', ''),
        'summary_zh': getattr(item, 'summary_zh', ''),
        'summary_en': getattr(item, 'summary_en', ''),
        'content_zh': getattr(item, 'content_zh', ''),
        'content_en': getattr(item, 'content_en', ''),
        'source_zh': getattr(item, 'source_zh', ''),
        'source_en': getattr(item, 'source_en', ''),
        'source_url': getattr(item, 'source_url', ''),
        'lang': getattr(item, 'lang', 'zh'),
        'category': getattr(item, 'category', 'news'),
        'published_at': getattr(item, 'published_at', ''),
        'created_at': getattr(item, 'created_at', ''),
        'quality': {
            'total_100': getattr(item, 'quality', {}).total_100 if hasattr(getattr(item, 'quality', {}), 'total_100') else 0,
            'grade': getattr(item, 'quality', {}).grade if hasattr(getattr(item, 'quality', {}), 'grade') else 'D',
            'scores': getattr(item, 'quality', {}).scores if hasattr(getattr(item, 'quality', {}), 'scores') else {},
        }
    }


def run_ai_calibration(news_list: List[Dict], skip_ai: bool = False) -> Tuple[List[Dict], Dict]:
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


def generate_tts_for_news(tts_service: TTSService, news: Dict) -> Tuple[List[Dict], Dict]:
    """
    使用统一 TTS 服务为单条新闻生成语音

    Returns:
        (tts_results, tts_stats)
    """
    voice_ids = list(VOICE_STYLES.keys())
    results, stats = tts_service.synthesize_for_news_sync(news, voice_ids)

    # 格式化输出
    output = []
    for r in results:
        # 从 audio_url 提取 voice_id (例如 /data/audio/xxx.mp3 -> xxx -> voice1)
        audio_url = r.get('audio_url', '')
        # 保持原有格式
        output.append({
            'news_id': r['news_id'],
            'voice_id': r['voice_id'],
            'audio_url': audio_url,
            'cached': r.get('cached', False),
            'engine': r.get('engine', 'unknown')
        })

    return output, {
        'minimax': stats.minimax,
        'edge_tts': stats.edge_tts,
        'cached': stats.cached,
        'failed': stats.failed
    }


def save_news_to_json(news_list: List[Dict], output_path: Path) -> None:
    """保存新闻到 JSON 文件"""
    # 分类统计
    category_stats = {'ai': 0, 'tools': 0, 'news': 0, 'product': 0}
    for n in news_list:
        cat = n.get('category', 'news')
        if cat in category_stats:
            category_stats[cat] += 1

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
        'categories': category_stats,
        'news': news_list
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"   保存到: {output_path}")


async def run_workflow_async(skip_tts: bool = False, skip_ai: bool = False, min_quality: int = 55):
    """运行完整工作流 (异步版本)"""
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
    news_items = await collect_news(min_quality=min_quality)

    if not news_items:
        print("\n❌ 没有收集到新闻")
        return

    # 转换为字典（已按分数排序）
    news_list = [news_item_to_dict(n) for n in news_items]
    print(f"   收集到 {len(news_list)} 条新闻")

    # [2/6] AI校准
    calibrated_news, calibration_stats = run_ai_calibration(news_list, skip_ai)

    # 按校准后分数重新排序
    calibrated_news.sort(key=lambda x: x['quality']['total_100'], reverse=True)

    # [3/6] 过滤极低分（校准后低于阈值）
    print(f"\n[3/6] 质量过滤...")
    filtered_news = [n for n in calibrated_news if n['quality']['total_100'] >= min_quality]
    print(f"   过滤后: {len(filtered_news)} 条")

    # TTS 生成
    tts_results = []
    tts_stats = {'minimax': 0, 'edge_tts': 0, 'cached': 0, 'failed': 0}

    if not skip_tts:
        print(f"\n[4/6] 生成语音 (4种风格)...")

        # 初始化 TTS 服务
        tts_service = get_tts_service(audio_dir)

        for i, news in enumerate(filtered_news):
            print(f"   [{i+1}/{len(filtered_news)}] {news['title_zh'][:30]}...")
            results, stats = generate_tts_for_news(tts_service, news)
            tts_results.extend(results)

            # 统计
            tts_stats['minimax'] += stats['minimax']
            tts_stats['edge_tts'] += stats['edge_tts']
            tts_stats['cached'] += stats['cached']
            tts_stats['failed'] += stats['failed']

            # 显示成功信息
            for r in results:
                voice_name = VOICE_STYLES.get(r['voice_id'], {}).get('name', r['voice_id'])
                engine = r.get('engine', 'unknown')
                if r.get('cached'):
                    print(f"      ✅ {voice_name} [缓存]")
                elif engine == 'minimax':
                    print(f"      ✅ {voice_name} [MiniMax]")
                elif engine == 'edge-tts':
                    print(f"      ✅ {voice_name} [edge-tts]")

        print(f"\n   📊 TTS统计:")
        print(f"      MiniMax: {tts_stats['minimax']} 个")
        print(f"      edge-tts: {tts_stats['edge_tts']} 个")
        print(f"      缓存: {tts_stats['cached']} 个")
        if tts_stats['failed'] > 0:
            print(f"      失败: {tts_stats['failed']} 个")
        print(f"      总计: {len(tts_results)} 个")
    else:
        print("\n[4/6] 跳过TTS生成")

    # 添加语音URL到新闻
    tts_map = {}
    for t in tts_results:
        news_id = t['news_id']
        if news_id not in tts_map:
            tts_map[news_id] = {}
        # voice_id 格式转换: cache_key -> voice1/voice2/voice3/voice4
        # 从 audio_url 提取 cache_key
        cache_key = t['audio_url'].split('/')[-1].replace('.mp3', '')
        # 重新映射到 voice_id
        for vid, style in VOICE_STYLES.items():
            import hashlib
            expected_key = hashlib.md5((news_id + vid).encode()).hexdigest()
            if cache_key == expected_key:
                tts_map[news_id][vid] = t['audio_url']
                break

    for news in filtered_news:
        news['audio'] = tts_map.get(news['id'], {})

    # [5/6] 保存
    print(f"\n[5/6] 保存新闻数据...")
    output_path = Path(__file__).parent.parent / "app" / "data" / "news.json"
    save_news_to_json(filtered_news, output_path)

    # [6/6] 完成
    print("\n[6/6] 完成!")
    print("-" * 50)
    print(f"✅ 总计: {len(filtered_news)} 条新闻")
    category_stats = {'ai': 0, 'tools': 0, 'news': 0, 'product': 0}
    for n in filtered_news:
        cat = n.get('category', 'news')
        if cat in category_stats:
            category_stats[cat] += 1
    print(f"   分类: AI({category_stats['ai']}) 工具({category_stats['tools']}) 动态({category_stats['news']}) 产品({category_stats['product']})")
    print(f"✅ 语音: {len(tts_results)} 个文件")
    if not skip_tts:
        print(f"   (MiniMax: {tts_stats['minimax']}, edge-tts: {tts_stats['edge_tts']}, 缓存: {tts_stats['cached']})")
    if not skip_ai and MINIMAX_API_KEY:
        print(f"✅ AI校准: 通过{calibration_stats.get('passed', 0)}, 修正{calibration_stats.get('adjusted', 0)}, 舍弃{calibration_stats.get('discarded', 0)}")


def run_workflow(skip_tts: bool = False, skip_ai: bool = False, min_quality: int = 55):
    """运行完整工作流 (同步入口)"""
    asyncio.run(run_workflow_async(skip_tts, skip_ai, min_quality))


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
