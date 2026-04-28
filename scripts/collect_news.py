#!/usr/bin/env python3
"""
TechEcho Pro - 新闻收集脚本

用法:
    python scripts/collect_news.py              # 收集所有新闻
    python scripts/collect_news.py --category ai  # 只收集AI类别
    python scripts/collect_news.py --lang zh    # 只收集中文新闻
    python scripts/collect_news.py --limit 50  # 限制数量
"""

import argparse
import asyncio
import json
import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

async def collect_news(category=None, lang=None, limit=None, min_quality=55):
    """收集新闻的主函数"""
    print("=" * 50)
    print("TechEcho Pro - 新闻收集工作流")
    print("=" * 50)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"分类: {category or '全部'}")
    print(f"语言: {lang or '全部'}")
    print(f"最低质量: {min_quality}")
    print("-" * 50)
    
    try:
        # 导入新闻收集服务
        from services.news_collector_v2 import BilingualNewsCollector
        
        collector = BilingualNewsCollector()
        
        print("\n[1/3] 初始化收集器...")
        
        print("\n[2/3] 收集新闻...")
        # 收集新闻
        news_items = await collector.collect_all(lang=lang, category=category)
        
        print(f"   收集到 {len(news_items)} 条原始新闻")
        
        print("\n[3/3] 过滤和排序...")
        # 过滤低质量新闻
        filtered = [n for n in news_items if (n.quality.total_100 if n.quality else 0) >= min_quality]
        print(f"   过滤后剩余 {len(filtered)} 条 (质量 >= {min_quality})")
        
        # 按质量分数排序
        filtered.sort(key=lambda x: x.quality.total_100 if x.quality else 0, reverse=True)
        
        # 限制数量
        if limit:
            filtered = filtered[:limit]
            print(f"   限制数量后: {len(filtered)} 条")
        
        # 转换为字典
        result = []
        for item in filtered:
            result.append({
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
            })
        
        # 保存到文件
        output_data = {
            'lastUpdate': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'totalCount': len(result),
            'stats': {
                'A+': len([n for n in result if n['quality']['grade'] == 'A+']),
                'A': len([n for n in result if n['quality']['grade'] == 'A']),
                'B': len([n for n in result if n['quality']['grade'] == 'B']),
                'C': len([n for n in result if n['quality']['grade'] == 'C']),
                'D': len([n for n in result if n['quality']['grade'] == 'D'])
            },
            'categories': list(set(n['category'] for n in result)),
            'news': result
        }
        
        # 保存到 app/data/news.json
        output_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'data', 'news.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print("-" * 50)
        print(f"✅ 完成! 保存到: {output_path}")
        print(f"   总计: {len(result)} 条新闻")
        print(f"   高质量 (A/B): {len([n for n in result if n['quality']['grade'] in ['A+', 'A', 'B']])} 条")
        
        return result
        
    except ImportError as e:
        print(f"\n⚠️  导入错误: {e}")
        print("   请确保已安装依赖: pip install -r requirements.txt")
        return []
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    parser = argparse.ArgumentParser(description='TechEcho Pro 新闻收集工具')
    parser.add_argument('--category', '-c', help='指定分类 (ai/tools/news/product)')
    parser.add_argument('--lang', '-l', help='指定语言 (zh/en)')
    parser.add_argument('--limit', type=int, help='限制新闻数量')
    parser.add_argument('--min-quality', type=int, default=55, help='最低质量分数 (默认55)')
    
    args = parser.parse_args()
    
    result = asyncio.run(collect_news(
        category=args.category,
        lang=args.lang,
        limit=args.limit,
        min_quality=args.min_quality
    ))
    
    sys.exit(0 if result else 1)

if __name__ == '__main__':
    main()
