"""
新闻质量分析器

从 news_collector_v2.py 抽取的独立质量评分模块
"""

import re
from typing import Dict, List

from src.config.sources import SOURCE_TIERS, CATEGORIES


class NewsQualityAnalyzer:
    """
    新闻质量分析器
    
    8 维度评分体系:
    - completeness: 内容完整性 (15%)
    - language: 语言质量 (15%)
    - title: 标题质量 (10%)
    - source_credibility: 来源权威性 (10%)
    - info_density: 信息密度 (10%)
    - actionability: 可操作性 (15%)
    - impact: 影响力 (15%)
    - originality: 独创性 (10%)
    """
    
    WEIGHTS = {
        "completeness": 0.15,
        "language": 0.15,
        "title": 0.10,
        "source_credibility": 0.10,
        "info_density": 0.10,
        "actionability": 0.15,
        "impact": 0.15,
        "originality": 0.10
    }
    
    def __init__(self):
        self.tier1 = SOURCE_TIERS.get("tier1", [])
        self.tier2 = SOURCE_TIERS.get("tier2", [])
    
    def analyze_quality(self, title: str, summary: str, source: str, url: str = "") -> Dict:
        """
        分析新闻质量
        
        Args:
            title: 标题
            summary: 摘要
            source: 来源名称
            url: 原文链接
            
        Returns:
            Dict: 包含 total_100, grade, scores, issues
        """
        scores = {
            "completeness": self._score_completeness(summary),
            "language": self._score_language(summary),
            "title": self._score_title(title, summary),
            "source_credibility": self._score_source(source),
            "info_density": self._score_density(summary),
            "actionability": self._score_actionability(summary),
            "impact": self._score_impact(summary),
            "originality": self._score_originality(summary),
        }
        
        # 加权总分
        weighted = sum(scores[k] * self.WEIGHTS[k] for k in self.WEIGHTS)
        total_100 = weighted * 10
        
        # 等级
        if total_100 >= 85: grade = "A+"
        elif total_100 >= 75: grade = "A"
        elif total_100 >= 65: grade = "B"
        elif total_100 >= 55: grade = "C"
        else: grade = "D"
        
        # 问题识别
        issues = []
        if scores['completeness'] < 6: issues.append("内容要素不完整")
        if scores['language'] < 6: issues.append("语言质量欠佳")
        if scores['actionability'] < 5: issues.append("缺乏可执行洞察")
        
        return {
            "total_100": round(total_100, 1),
            "weighted_total": round(weighted, 2),
            "grade": grade,
            "scores": {k: round(v, 1) for k, v in scores.items()},
            "issues": issues
        }
    
    def _score_completeness(self, text: str) -> float:
        """内容完整性 (5W1H)"""
        score = 0.0
        elements = {
            "who": r'(公司|团队|机构|发布|宣布)',
            "what": r'(发布|推出|收购|融资|合作)',
            "when": r'(\d+年|\d+月|\d+日|今天|昨天)',
            "where": r'(中国|美国|全球|北京|上海)',
            "how": r'(通过|使用|采用|方式|技术)',
        }
        present = sum(1 for p in elements.values() if re.search(p, text))
        score = present * 1.5
        if re.search(r'\d+[%亿]', text): score += 0.5
        return min(10, score)
    
    def _score_language(self, text: str) -> float:
        """语言质量"""
        score = 8.0
        if re.search(r'\bthe\b', text, re.I): score -= 0.5
        if re.search(r'的\s*的', text): score -= 1.0
        marketing = ['关注', '公众号', '微信', '扫码']
        if any(p in text for p in marketing): score -= 2.0
        return max(0, min(10, score))
    
    def _score_title(self, title: str, content: str) -> float:
        """标题质量"""
        score = 7.0
        if 15 <= len(title) <= 30: score += 1.5
        if title.endswith('...') or title.endswith('…'): score -= 1.0
        clickbait = ['震惊', '刚刚', '内幕', '必看']
        if any(p in title for p in clickbait): score -= 2.0
        return max(0, min(10, score))
    
    def _score_source(self, source: str) -> float:
        """来源权威性"""
        score = 5.0
        if any(s in source for s in self.tier1): score += 4.0
        elif any(s in source for s in self.tier2): score += 2.5
        return max(0, min(10, score))
    
    def _score_density(self, text: str) -> float:
        """信息密度"""
        count = 0
        if re.search(r'\d+[%亿万千]', text): count += 1
        if re.search(r'[一-龥]{2,6}(公司|集团|机构)', text): count += 1
        if re.search(r'(AI|模型|技术|功能)', text): count += 1
        if re.search(r'(发布|推出|收购|融资)', text): count += 1
        return min(10, count * 2.5)
    
    def _score_actionability(self, text: str) -> float:
        """可操作性"""
        score = 5.0
        action = ['如何使用', '教程', '指南', '方法', '建议']
        if any(p in text for p in action): score += 2.0
        if re.search(r'\d+[%亿]', text): score += 1.0
        return max(0, min(10, score))
    
    def _score_impact(self, text: str) -> float:
        """影响力"""
        score = 5.0
        high = ['突破', '首创', '首次', '最大', '改变', '颠覆']
        score += sum(0.5 for p in high if p in text)
        return max(0, min(10, score))
    
    def _score_originality(self, text: str) -> float:
        """独创性"""
        score = 5.0
        orig = ['分析', '解读', '观点', '独家', '深度']
        if any(p in text for p in orig): score += 2.0
        if '编译' in text or '转载' in text: score -= 1.5
        return max(0, min(10, score))
