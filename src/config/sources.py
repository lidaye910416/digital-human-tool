"""
新闻源配置

统一管理所有新闻采集源配置
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


# ===== RSS 源配置 =====

RSS_SOURCES_ZH: List[Dict] = [
    {"name": "钛媒体", "url": "https://www.tmtpost.com/rss", "category": "news", "weight": 3.0, "language": "zh"},
    {"name": "爱范儿", "url": "https://www.ifanr.com/feed", "category": "product", "weight": 3.0, "language": "zh"},
    {"name": "少数派", "url": "https://sspai.com/feed", "category": "product", "weight": 3.0, "language": "zh"},
    {"name": "Solidot", "url": "https://www.solidot.org/index.rss", "category": "news", "weight": 2.5, "language": "zh"},
    {"name": "虎嗅", "url": "https://www.huxiu.com/rss/0.xml", "category": "news", "weight": 2.5, "language": "zh"},
    {"name": "36氪", "url": "https://36kr.com/feed", "category": "news", "weight": 2.5, "language": "zh"},
]

RSS_SOURCES_EN: List[Dict] = [
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "category": "news", "weight": 2.5, "language": "en"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/", "category": "ai", "weight": 2.5, "language": "en"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index", "category": "tools", "weight": 2.0, "language": "en"},
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "category": "product", "weight": 2.0, "language": "en"},
    {"name": "Hacker News", "url": "https://hnrss.org/frontpage", "category": "news", "weight": 2.0, "language": "en"},
    {"name": "Wired", "url": "https://www.wired.com/feed/rss", "category": "ai", "weight": 2.0, "language": "en"},
]

RSS_SOURCES = RSS_SOURCES_ZH + RSS_SOURCES_EN


# ===== 固定网站爬取配置 =====

WEB_SITES: List[Dict] = [
    # {
    #     "name": "示例网站",
    #     "url": "https://example.com/news",
    #     "category": "news",
    #     "weight": 2.0,
    #     "language": "zh",
    #     "enabled": False,
    #     "selectors": {
    #         "list": ".news-list .item",
    #         "title": ".title",
    #         "content": ".content",
    #         "link": "a",
    #     },
    #     "pagination": {
    #         "enabled": True,
    #         "next": ".pagination .next",
    #         "max_pages": 3,
    #     }
    # },
]


# ===== API 数据源配置 =====

API_SOURCES: List[Dict] = [
    # {
    #     "name": "示例API",
    #     "url": "https://api.example.com/news",
    #     "category": "news",
    #     "weight": 2.0,
    #     "language": "zh",
    #     "enabled": False,
    #     "headers": {"Authorization": "Bearer xxx"},
    #     "mapping": {
    #         "title": "title",
    #         "content": "content",
    #         "published_at": "publishedAt",
    #     }
    # },
]


# ===== 分类配置 =====

CATEGORIES: Dict[str, Dict] = {
    "ai": {
        "name": "AI人工智能",
        "keywords": ["AI", "LLM", "GPT", "ChatGPT", "OpenAI", "Anthropic", "Claude", "Gemini",
                     "人工智能", "大模型", "深度学习", "神经网络", "AIGC", "AGI", "模型训练",
                     "机器学习", "自然语言处理", "计算机视觉", "AI应用", "AI工具", "AI产品"]
    },
    "tools": {
        "name": "开发工具",
        "keywords": ["GitHub", "VS Code", "API", "SDK", "框架", "Python", "JavaScript", "Rust",
                     "编程", "开发", "开源", "代码", "IDE", "编译器", "Docker", "Kubernetes",
                     "Git", "数据库", "云服务", "AWS", "Azure", "GCP", "Vercel", "Netlify"]
    },
    "news": {
        "name": "科技动态",
        "keywords": ["发布", "收购", "融资", "裁员", "上市", "合作", "投资", "财报", "业绩",
                     "战略", "转型", "布局", "数字经济", "产业数字化", "数字化转型",
                     "科技公司", "互联网", "半导体", "芯片", "新能源", "电动汽车"]
    },
    "product": {
        "name": "产品设计",
        "keywords": ["产品", "设计", "UI", "UX", "App", "Launch", "发布", "更新", "版本",
                     "软件", "应用", "小程序", "网站", "平台", "功能", "界面", "交互",
                     "苹果", "谷歌", "微软", "Meta", "产品发布", "新功能"]
    }
}


# ===== 过滤配置 =====

UNRELATED_KEYWORDS: List[str] = [
    "游戏", "电竞", "娱乐", "电影", "音乐", "体育", "八卦", "明星",
    "game", "gaming", "entertainment", "movie", "music", "sports", "celebrity"
]

# ===== 评分关键词配置 =====

QUALITY_KEYWORDS = {
    "clickbait": ["震惊", "刚刚", "内幕", "必看", "突发", "重磅", "爆料", "曝光"],
    "marketing": ["关注", "公众号", "微信", "扫码", "转发", "扩散"],
    "high_impact": ["突破", "首创", "首次", "最大", "改变", "颠覆", "革命", "领先"],
    "originality": ["分析", "解读", "观点", "独家", "深度", "内幕", "揭秘"],
    "actionability": ["如何使用", "教程", "指南", "方法", "建议", "技巧", "窍门"],
}

# ===== 内容完整性要素 (5W1H) =====

COMPLETENESS_PATTERNS = {
    "who": r'(公司|团队|机构|发布|宣布)',
    "what": r'(发布|推出|收购|融资|合作)',
    "when": r'(\d+年|\d+月|\d+日|今天|昨天)',
    "where": r'(中国|美国|全球|北京|上海)',
    "how": r'(通过|使用|采用|方式|技术)',
}

# ===== 信息密度指标 =====

DENSITY_PATTERNS = {
    "numbers": r'\d+[%亿万千]',  # 数字
    "company": r'[一-龥]{2,6}(公司|集团|机构)',  # 公司实体
    "tech": r'(AI|模型|技术|功能)',  # 技术术语
    "action": r'(发布|推出|收购|融资)',  # 动作词
}


def get_categories() -> Dict[str, Dict]:
    """获取分类配置"""
    return CATEGORIES


def get_source_tiers() -> Dict[str, List[str]]:
    """获取来源层级"""
    return SOURCE_TIERS


def get_filter_keywords() -> List[str]:
    """获取过滤关键词"""
    return UNRELATED_KEYWORDS


def get_quality_keywords() -> Dict[str, List[str]]:
    """获取评分关键词"""
    return QUALITY_KEYWORDS


def get_tier_for_source(source_name: str) -> int:
    """根据来源名称获取层级 (1=顶级, 2=二级, 0=未知)"""
    for tier_name, sources in SOURCE_TIERS.items():
        if source_name in sources:
            return 1 if tier_name == "tier1" else 2
    return 0


# ===== 来源权威性 =====

SOURCE_TIERS: Dict[str, List[str]] = {
    "tier1": ['钛媒体', '爱范儿', '少数派', 'Solidot', '36氪', '虎嗅', 'MIT Tech Review'],
    "tier2": ['TechCrunch', 'The Verge', 'Ars Technica', 'Wired', 'BBC', 'Reuters'],
}


def get_sources(language: Optional[str] = None) -> List[Dict]:
    """获取所有启用的源"""
    all_sources = []
    
    # RSS 源
    if language is None or language == "zh":
        all_sources.extend(RSS_SOURCES_ZH)
    if language is None or language == "en":
        all_sources.extend(RSS_SOURCES_EN)
    
    # 固定网站
    for site in WEB_SITES:
        if site.get("enabled", False):
            if language is None or site.get("language") == language:
                all_sources.append(site)
    
    # API 源
    for api in API_SOURCES:
        if api.get("enabled", False):
            if language is None or api.get("language") == language:
                all_sources.append(api)
    
    return all_sources
