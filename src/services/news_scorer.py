"""
新闻质量评分器 - 8维度规则评分

职责: 对 NewsItem 进行质量评分，不涉及数据获取和存储
"""

import re
import logging
from typing import Dict
from src.models.news_bilingual import NewsItem, QualityScore
from src.config.sources import (
    get_quality_keywords, get_tier_for_source,
    COMPLETENESS_PATTERNS, DENSITY_PATTERNS
)

logger = logging.getLogger(__name__)


class NewsScorer:
    """
    新闻质量评分器
    
    8 维度评分体系:
    - completeness: 内容完整性 (5W1H)
    - language: 语言质量
    - title: 标题质量
    - source_credibility: 来源权威性
    - info_density: 信息密度
    - actionability: 可操作性
    - impact: 影响力
    - originality: 独创性
    """
    
    # 权重配置
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
    
    # 等级阈值
    THRESHOLDS = {
        "grade_A_plus": 85,
        "grade_A": 75,
        "grade_B": 65,
        "grade_C": 55,
    }
    
    def score(self, news: NewsItem) -> QualityScore:
        """
        对新闻进行质量评分
        
        Args:
            news: NewsItem 对象
        
        Returns:
            QualityScore 评分结果
        """
        # 获取内容
        title = news.title_zh or news.title_en or ""
        summary = news.summary_zh or news.summary_en or ""
        content = news.content_zh or news.content_en or ""
        source = news.source_zh or news.source_en or ""
        
        # 合并文本用于评分
        text = f"{title} {summary} {content}"
        
        # 计算各维度分数
        scores = {
            "completeness": self._score_completeness(summary),
            "language": self._score_language(text),
            "title": self._score_title(title, summary),
            "source_credibility": self._score_source(source),
            "info_density": self._score_density(text),
            "actionability": self._score_actionability(text),
            "impact": self._score_impact(text),
            "originality": self._score_originality(text),
        }
        
        # 加权总分
        weighted = sum(scores[k] * self.WEIGHTS[k] for k in self.WEIGHTS)
        total_100 = weighted * 10
        
        # 等级判定
        grade = self._calculate_grade(total_100)
        
        # 问题识别
        issues = self._identify_issues(scores)
        
        return QualityScore(
            total_100=round(total_100, 1),
            weighted_total=round(weighted, 2),
            grade=grade,
            scores={k: round(v, 1) for k, v in scores.items()},
            issues=issues
        )
    
    def score_batch(self, news_list: list) -> list:
        """批量评分"""
        for news in news_list:
            news.quality = self.score(news)
        return news_list
    
    def _calculate_grade(self, score: float) -> str:
        """根据分数计算等级"""
        if score >= self.THRESHOLDS["grade_A_plus"]: return "A+"
        elif score >= self.THRESHOLDS["grade_A"]: return "A"
        elif score >= self.THRESHOLDS["grade_B"]: return "B"
        elif score >= self.THRESHOLDS["grade_C"]: return "C"
        else: return "D"
    
    def _identify_issues(self, scores: Dict) -> list:
        """识别问题"""
        issues = []
        if scores['completeness'] < 6: issues.append("内容要素不完整")
        if scores['language'] < 6: issues.append("语言质量欠佳")
        if scores['actionability'] < 5: issues.append("缺乏可执行洞察")
        return issues
    
    def _score_completeness(self, text: str) -> float:
        """内容完整性 (5W1H)"""
        if not text:
            return 0.0
        score = 0.0
        present = sum(1 for p in COMPLETENESS_PATTERNS.values() if re.search(p, text))
        score = present * 1.5
        if re.search(r'\d+[%亿万千]', text): score += 0.5
        return min(10, max(0, score))
    
    def _score_language(self, text: str) -> float:
        """语言质量"""
        score = 8.0
        if re.search(r'\bthe\b', text, re.I): score -= 0.5
        if re.search(r'的\s*的', text): score -= 1.0
        quality_kw = get_quality_keywords()
        marketing = quality_kw.get("marketing", [])
        if any(p in text for p in marketing): score -= 2.0
        return max(0, min(10, score))
    
    def _score_title(self, title: str, content: str) -> float:
        """标题质量"""
        score = 7.0
        if 15 <= len(title) <= 30: score += 1.5
        if title.endswith('...') or title.endswith('…'): score -= 1.0
        quality_kw = get_quality_keywords()
        clickbait = quality_kw.get("clickbait", [])
        if any(p in title for p in clickbait): score -= 2.0
        return max(0, min(10, score))
    
    def _score_source(self, source: str) -> float:
        """来源权威性"""
        score = 5.0
        tier = get_tier_for_source(source)
        if tier == 1: score += 4.0
        elif tier == 2: score += 2.5
        return max(0, min(10, score))
    
    def _score_density(self, text: str) -> float:
        """信息密度"""
        if not text:
            return 0.0
        count = 0
        for key, pattern in DENSITY_PATTERNS.items():
            if re.search(pattern, text): count += 1
        return min(10, count * 2.5)
    
    def _score_actionability(self, text: str) -> float:
        """可操作性"""
        score = 5.0
        quality_kw = get_quality_keywords()
        action = quality_kw.get("actionability", [])
        if any(p in text for p in action): score += 2.0
        if re.search(r'\d+[%亿万千]', text): score += 1.0
        return max(0, min(10, score))
    
    def _score_impact(self, text: str) -> float:
        """影响力"""
        score = 5.0
        quality_kw = get_quality_keywords()
        high = quality_kw.get("high_impact", [])
        score += sum(0.5 for p in high if p in text)
        return max(0, min(10, score))
    
    def _score_originality(self, text: str) -> float:
        """独创性"""
        score = 5.0
        quality_kw = get_quality_keywords()
        orig = quality_kw.get("originality", [])
        if any(p in text for p in orig): score += 2.0
        if '编译' in text or '转载' in text: score -= 1.5
        return max(0, min(10, score))


# 全局实例
scorer = NewsScorer()
