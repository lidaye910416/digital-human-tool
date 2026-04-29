#!/usr/bin/env python3
"""
新闻采集测试脚本（含 AI 校准）

测试收集功能，保存结果供人工检查
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.services.news_collector import NewsCollector
from src.services.news_collector_rss import BilingualRSSCollector


async def test_rss_collector():
    """测试 RSS 采集器"""
    print("\n" + "=" * 60)
    print("测试 1: RSS 采集器 (BilingualRSSCollector)")
    print("=" * 60)
    
    collector = BilingualRSSCollector()
    
    # 分别收集中文和英文
    print("\n[1.1] 收集中文新闻...")
    zh_items = await collector.collect_zh()
    print(f"   收集到 {len(zh_items)} 条中文新闻")
    
    print("\n[1.2] 收集英文新闻...")
    en_items = await collector.collect_en()
    print(f"   收集到 {len(en_items)} 条英文新闻")
    
    print("\n[1.3] 收集双语新闻...")
    all_items = await collector.collect_all()
    print(f"   共 {len(all_items)} 条新闻")
    
    # 去重测试
    dedup_items = BilingualRSSCollector.deduplicate(all_items)
    print(f"   去重后 {len(dedup_items)} 条新闻")
    
    await collector.close()
    
    return dedup_items


def news_item_to_dict(item):
    """将 NewsItem 转换为字典"""
    quality = item.quality if item.quality else None
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
        'created_at': getattr(item, 'created_at', ''),
        'weight': item.weight,
        'quality': {
            'total_100': quality.total_100 if quality else 0,
            'grade': quality.grade if quality else 'D',
            'scores': quality.scores if quality else {},
            'ai_calibrated': getattr(quality, 'ai_calibrated', False),
            'calibration_reason': getattr(quality, 'calibration_reason', ''),
            'content_refined': getattr(quality, 'content_refined', False),
        } if quality else {'total_100': 0, 'grade': 'D', 'scores': {}}
    }


async def test_ai_calibration(items):
    """测试 AI 校准"""
    print("\n" + "=" * 60)
    print("测试 2: AI 质量校准 (MiniMax)")
    print("=" * 60)
    
    try:
        from src.services.news_ai_calibrator import NewsAICalibrator
        from src.config import MINIMAX_API_KEY
        
        if not MINIMAX_API_KEY:
            print("   ⚠️  MINIMAX_API_KEY 未配置，跳过 AI 校准")
            return [news_item_to_dict(i) for i in items], None
        
        # 将 NewsItem 转换为字典
        news_list = [news_item_to_dict(i) for i in items]
        
        print(f"\n   原始新闻数量: {len(news_list)} 条")
        
        # 统计校准前分数分布
        before_grades = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0}
        for n in news_list:
            grade = n['quality']['grade']
            if grade in before_grades:
                before_grades[grade] += 1
        print(f"\n   校准前分数分布: {before_grades}")
        
        # 创建 AI 校准器
        calibrator = NewsAICalibrator(MINIMAX_API_KEY)
        
        # 执行 AI 校准（限制数量避免超时）
        max_items = min(len(news_list), 20)  # 最多处理 20 条
        print(f"\n   执行 AI 校准中... (处理前 {max_items} 条)")
        
        news_to_calibrate = news_list[:max_items]
        calibrated_news, stats = calibrator.batch_calibrate(news_to_calibrate, min_score=0)
        
        # 剩余未校准的新闻直接加入
        if len(news_list) > max_items:
            calibrated_news.extend(news_list[max_items:])
        
        print(f"\n   📊 AI 校准统计:")
        print(f"      处理: {max_items} 条")
        print(f"      通过: {stats.get('passed', 0)} 条")
        print(f"      修正分数: {stats.get('adjusted', 0)} 条")
        print(f"      内容润色: {stats.get('content_refined', 0)} 条")
        print(f"      舍弃: {stats.get('discarded', 0)} 条")
        
        # 统计校准后分数分布
        after_grades = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0}
        for n in calibrated_news:
            grade = n.get('quality', {}).get('grade', 'D')
            if grade in after_grades:
                after_grades[grade] += 1
        print(f"\n   校准后分数分布: {after_grades}")
        
        # 显示分类修正
        categories = stats.get('categories', {})
        print(f"\n   分类分布: AI({categories.get('ai', 0)}) 工具({categories.get('tools', 0)}) 动态({categories.get('news', 0)}) 产品({categories.get('product', 0)})")
        
        return calibrated_news, stats
        
    except Exception as e:
        print(f"   ❌ AI 校准失败: {e}")
        import traceback
        traceback.print_exc()
        return [news_item_to_dict(i) for i in items], None


def save_results(calibrated_items, filtered_items, stats):
    """保存测试结果"""
    output_dir = Path(__file__).parent
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 统计信息
    categories = {}
    grades = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0}
    for item in calibrated_items:
        cat = item.get('category', 'news')
        categories[cat] = categories.get(cat, 0) + 1
        grade = item.get('quality', {}).get('grade', 'D')
        if grade in grades:
            grades[grade] += 1
    
    output_data = {
        "timestamp": timestamp,
        "total_count": len(calibrated_items),
        "stats": {
            "categories": categories,
            "grades": grades,
            "ai_calibration": stats if stats else {}
        },
        "news": calibrated_items,
        "filtered_news": filtered_items
    }
    
    # 保存 JSON
    json_path = output_dir / f"collected_news_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 保存到: {json_path}")
    
    # 保存详细报告
    report_path = output_dir / f"test_report_{timestamp}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# 新闻采集测试报告\n\n")
        f.write(f"**测试时间**: {timestamp}\n\n")
        f.write(f"## 统计信息\n\n")
        f.write(f"- 总数: {len(calibrated_items)} 条\n")
        f.write(f"- 分类统计: {categories}\n")
        f.write(f"- 质量分布: {grades}\n")
        
        if stats:
            f.write(f"\n## AI 校准统计\n\n")
            f.write(f"- 处理: 前 20 条\n")
            f.write(f"- 通过: {stats.get('passed', 0)} 条\n")
            f.write(f"- 修正分数: {stats.get('adjusted', 0)} 条\n")
            f.write(f"- 内容润色: {stats.get('content_refined', 0)} 条\n")
            f.write(f"- 舍弃: {stats.get('discarded', 0)} 条\n")
        
        f.write(f"\n## AI 校准详情\n\n")
        
        # 显示经过 AI 校准的新闻
        ai_calibrated = [n for n in calibrated_items if n.get('quality', {}).get('ai_calibrated')]
        
        if ai_calibrated:
            for i, news in enumerate(ai_calibrated[:10], 1):
                title = news.get('title_zh') or news.get('title_en', '无标题')
                quality = news.get('quality', {})
                
                f.write(f"### {i}. {title}\n\n")
                f.write(f"- **分类**: {news.get('category', 'news')}")
                if quality.get('ai_calibrated'):
                    f.write(f" ✅")
                f.write(f"\n")
                f.write(f"- **语言**: {news.get('lang', 'zh')}\n")
                f.write(f"- **来源**: {news.get('source_zh') or news.get('source_en', '')}\n")
                f.write(f"- **原始质量**: {quality.get('original_score', quality.get('total_100', 0))}分\n")
                f.write(f"- **校准后质量**: {quality.get('total_100', 0)}分 ({quality.get('grade', 'D')})\n")
                
                if quality.get('calibration_reason'):
                    f.write(f"- **校准理由**: {quality.get('calibration_reason')}\n")
                
                if quality.get('content_refined'):
                    f.write(f"- **✨ 内容已润色**\n")
                    if news.get('title_zh'):
                        f.write(f"- **润色后标题**: {news.get('title_zh')}\n")
                
                summary = news.get('summary_zh') or news.get('summary_en', '')
                if summary:
                    f.write(f"- **摘要**: {summary[:200]}...\n")
                
                f.write(f"\n---\n\n")
        else:
            f.write("无 AI 校准数据\n\n")
        
        f.write(f"\n## 全部新闻 (按质量排序)\n\n")
        
        # 按质量排序显示所有
        sorted_items = sorted(calibrated_items, key=lambda x: x.get('quality', {}).get('total_100', 0), reverse=True)
        
        for i, news in enumerate(sorted_items[:30], 1):
            title = news.get('title_zh') or news.get('title_en', '无标题')
            quality = news.get('quality', {})
            ai_flag = "🤖" if quality.get('ai_calibrated') else ""
            
            f.write(f"**{i}.** {title} {ai_flag}\n")
            f.write(f"   - 质量: {quality.get('total_100', 0)}分 ({quality.get('grade', 'D')}) | 分类: {news.get('category', 'news')} | 来源: {news.get('source_zh') or news.get('source_en', '')}\n\n")
    
    print(f"✅ 报告保存到: {report_path}")
    
    return json_path, report_path


async def main():
    print("=" * 60)
    print("新闻采集功能测试 (含 AI 校准)")
    print("=" * 60)
    
    # 测试 1: RSS 采集器
    items = await test_rss_collector()
    
    # 测试 2: AI 校准
    calibrated_items, stats = await test_ai_calibration(items)
    
    # 质量过滤 (>=60分)
    print("\n" + "=" * 60)
    print("质量过滤 (>=60分)")
    print("=" * 60)
    
    filtered_items = [n for n in calibrated_items if n.get('quality', {}).get('total_100', 0) >= 60]
    print(f"\n过滤后 {len(filtered_items)} 条新闻 (总共 {len(calibrated_items)} 条)")
    
    # 保存结果
    print("\n" + "=" * 60)
    print("保存测试结果")
    print("=" * 60)
    
    json_path, report_path = save_results(calibrated_items, filtered_items, stats)
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
    print(f"\n请检查以下文件:")
    print(f"1. JSON 数据: {json_path}")
    print(f"2. 详细报告: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
