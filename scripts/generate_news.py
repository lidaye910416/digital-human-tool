#!/usr/bin/env python3
"""生成双语新闻数据"""

import asyncio
import json
import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.news_collector_v2 import BilingualNewsCollector, ZH_SOURCES, EN_SOURCES


async def generate_bilingual_news():
    """生成双语新闻数据"""
    print("=" * 80)
    print("📰 Tech Echo - 双语新闻生成")
    print("=" * 80)
    
    collector = BilingualNewsCollector()
    
    try:
        # 收集中文新闻
        print("\n📡 收集中文新闻...")
        zh_news = await collector.collect_zh()
        print(f"   收集到 {len(zh_news)} 条中文新闻")
        
        # 收集英文新闻
        print("\n📡 收集英文新闻...")
        en_news = await collector.collect_en()
        print(f"   收集到 {len(en_news)} 条英文新闻")
        
        # 合并去重
        all_news = zh_news + en_news
        print(f"\n📊 合并后共 {len(all_news)} 条新闻")
        
        # 按质量排序
        all_news.sort(key=lambda x: x.quality.total_100, reverse=True)
        
        # 统计
        grades = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0}
        for item in all_news:
            if item.quality.grade in grades:
                grades[item.quality.grade] += 1
        
        print("\n📊 质量分布:")
        for grade in ["A+", "A", "B", "C", "D"]:
            count = grades[grade]
            pct = count / len(all_news) * 100 if all_news else 0
            bar = "█" * count
            print(f"   {grade}: {bar} {count} ({pct:.1f}%)")
        
        # 生成前端数据
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        os.makedirs(output_dir, exist_ok=True)
        
        # 转换为字典
        news_data = {
            "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "totalCount": len(all_news),
            "stats": grades,
            "categories": ["ai", "tools", "news", "product"],
            "news": [item.to_dict() for item in all_news[:50]]
        }
        
        # 保存 JSON
        json_path = os.path.join(output_dir, 'news_bilingual.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 JSON 数据已保存: {json_path}")
        
        # 保存 JS
        js_path = os.path.join(output_dir, 'news_output.js')
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(f'const NEWS_DATA = {json.dumps(news_data, ensure_ascii=False, indent=2)};')
        print(f"💾 JS 数据已保存: {js_path}")
        
        # 输出 TOP 5
        print("\n" + "=" * 80)
        print("🏆 TOP 5 高质量新闻")
        print("=" * 80)
        for i, item in enumerate(all_news[:5], 1):
            print(f"\n{i}. [{item.quality.grade} {item.quality.total_100}分]")
            print(f"   中文: {item.title_zh or item.title_en}")
            print(f"   英文: {item.title_en or item.title_zh}")
            print(f"   来源: {item.source_zh or item.source_en}")
        
        print("\n" + "=" * 80)
        print("✅ 生成完成!")
        
    finally:
        await collector.close()


if __name__ == "__main__":
    asyncio.run(generate_bilingual_news())
