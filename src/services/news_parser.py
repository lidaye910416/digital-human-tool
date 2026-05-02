"""
新闻数据解析层 - 将原始数据转换为 NewsItem

职责: 解析原始数据，过滤无效条目，生成 NewsItem
"""

import re
import logging
from typing import Dict, Optional
from datetime import datetime
from src.models.news_bilingual import NewsItem

logger = logging.getLogger(__name__)


class NewsParser:
    """新闻解析器"""
    
    def __init__(self):
        pass
    
    def parse(self, raw: Dict, lang: str = 'zh') -> Optional[NewsItem]:
        """
        将原始数据解析为 NewsItem
        
        Args:
            raw: 原始数据字典，包含 title, link, summary, published, _source 等
            lang: 语言 'zh' 或 'en'
        
        Returns:
            NewsItem 或 None（如果解析失败）
        """
        try:
            title = raw.get('title', '')[:200]
            if not title:
                return None
            
            # 清理 HTML
            content = self._clean_html(raw.get('summary', ''))
            summary = content[:300] if content else ""
            
            # 获取来源信息
            source_info = raw.get('_source', {})
            source_name = source_info.get('name', '') if isinstance(source_info, dict) else ''
            
            # 创建 NewsItem
            news = NewsItem(
                id=raw.get('id', ''),
                title_zh=title if lang == 'zh' else "",
                title_en=title if lang == 'en' else "",
                content_zh=content if lang == 'zh' else "",
                content_en=content if lang == 'en' else "",
                summary_zh=summary if lang == 'zh' else "",
                summary_en=summary if lang == 'en' else "",
                source_zh=source_name if lang == 'zh' else "",
                source_en=source_name if lang == 'en' else "",
                source_url=raw.get('link', ''),
                lang=lang,
                category=source_info.get('category', 'news') if isinstance(source_info, dict) else 'news',
                published_at=raw.get('published', ''),
                created_at=datetime.now().isoformat(),
                weight=source_info.get('weight', 1.0) if isinstance(source_info, dict) else 1.0
            )
            
            return news
            
        except Exception as e:
            logger.warning(f"Failed to parse news item: {e}")
            return None
    
    def parse_list(self, raw_list: list, lang: str = 'zh') -> list:
        """批量解析"""
        items = []
        for raw in raw_list:
            item = self.parse(raw, lang)
            if item:
                items.append(item)
        return items
    
    def _clean_html(self, text: str) -> str:
        """清理 HTML 标签"""
        if not text:
            return ""
        # 移除 HTML 标签
        text = re.sub(r'<[^>]+>', '', text)
        # 清理多余空白
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def deduplicate(self, items: list) -> list:
        """去重"""
        seen_titles = set()
        unique_items = []
        
        for item in items:
            norm_title = re.sub(r'[^一-龥a-zA-Z0-9]', '', item.title_zh or item.title_en)
            norm_title = norm_title.lower()[:30]
            
            if norm_title and norm_title not in seen_titles:
                seen_titles.add(norm_title)
                unique_items.append(item)
        
        return unique_items
