"""
TechEcho Pro - AI质量校准器

功能:
1. 基于规则评分结果，使用AI进行二次校准
2. 分类验证与修正
3. 过滤无关内容（如游戏、娱乐）
4. 自动修正明显错误的分数
5. 内容润色 - 清理无效信息，输出简洁干净的新闻

使用 MiniMax 2.7 模型
"""

import os
import json
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# MiniMax API 配置
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimax.chat/v1"
MINIMAX_DAILY_LIMIT = 11000  # 免费用户每日限制

# 四大目标分类
TARGET_CATEGORIES = {
    "ai": {
        "name": "AI人工智能",
        "description": "AI基础能力、大模型、机器学习相关",
        "keywords": ["AI", "LLM", "GPT", "ChatGPT", "OpenAI", "Anthropic", "Claude", "Gemini",
                    "人工智能", "大模型", "深度学习", "神经网络", "AIGC", "AGI", "模型训练",
                    "机器学习", "自然语言处理", "计算机视觉", "AI应用", "AI工具", "AI产品",
                    "大模型", "语言模型", "视觉模型", "多模态", "AI芯片", "AI服务器", "AI算力",
                    "AIGC", "生成式AI", "ChatGPT", "Sora", "文生图", "文生视频", "Agent", "智能体"]
    },
    "tools": {
        "name": "开发工具",
        "description": "前沿科技工具、开发框架、API服务",
        "keywords": ["GitHub", "VS Code", "API", "SDK", "框架", "Python", "JavaScript", "Rust",
                    "编程", "开发", "开源", "代码", "IDE", "编译器", "Docker", "Kubernetes",
                    "Git", "数据库", "云服务", "AWS", "Azure", "GCP", "Vercel", "Netlify",
                    "低代码", "SaaS", "PaaS", "IaaS", "云原生", "Serverless", "API网关",
                    "开发者平台", "开源社区", "代码托管", "CI/CD", "DevOps", "自动化部署"]
    },
    "news": {
        "name": "科技动态",
        "description": "数字产业、产业数字化动态",
        "keywords": ["数字产业", "产业数字化", "数字产业化", "数字化转型", "数字经济",
                    "数字中国", "智慧城市", "智慧医疗", "智慧教育", "智慧交通", "智慧政务",
                    "信息化", "数据要素", "数据中心", "云计算", "大数据", "物联网", "区块链",
                    "半导体", "芯片", "集成电路", "晶圆厂", "光刻机", "GPU", "CPU", "AI芯片",
                    "新能源", "电动汽车", "自动驾驶", "动力电池", "智能网联",
                    "发布", "收购", "融资", "上市", "合作", "投资", "财报", "业绩", "财报",
                    "科技公司", "互联网", "运营商", "设备商", "软件商", "方案商",
                    "战略合作", "数字化战略", "智能化战略", "转型", "布局", "落地", "应用"],
        # 排除关键词 - 泛战略、与科技无关的内容
        "exclude_keywords": ["房地产", "零售", "餐饮", "服装", "美妆", "母婴", "教育(非AI/数字化教育)"]
    },
    "product": {
        "name": "产品设计",
        "description": "优秀软件产品、设计创新",
        "keywords": ["产品", "设计", "UI", "UX", "App", "Launch", "发布", "更新", "版本",
                    "软件", "应用", "小程序", "网站", "平台", "功能", "界面", "交互",
                    "苹果", "谷歌", "微软", "Meta", "产品发布", "新功能", "Beta", "内测",
                    "SaaS产品", "软件更新", "版本更新", "功能更新", "界面改版", "交互优化"]
    }
}

# 过滤无关分类
UNRELATED_CATEGORIES = [
    # 游戏/娱乐
    "game", "gaming", "entertainment", "movie", "music", "sports", "anime", "comic",
    "游戏", "娱乐", "电影", "音乐", "体育", "八卦", "明星", "综艺", "电视剧", "演唱会",
    # 生活消费
    "food", "restaurant", "fashion", "beauty", "shopping", "retail", "e-commerce",
    "美食", "餐饮", "服装", "美妆", "购物", "零售", "电商", "母婴", "育儿",
    # 财经金融 (非科技)
    "banking", "bank", "insurance", "investment", "stock", "finance",
    "银行", "保险", "投资", "股票", "证券", "基金", "理财", "外汇", "期货",
    # 健康医疗 (非AI/数字化)
    "health", "medical", "hospital", "disease", "doctor", "medicine",
    "健康", "医疗", "医院", "疾病", "医生", "药品", "养生", "减肥", "美容(医疗)",
    # 房地产
    "real estate", "property", "housing", "apartment",
    "房地产", "房产", "房价", "楼市", "住宅", "买房", "卖房", "租房",
    # 社会生活
    "politics", "politician", "government", "law", "crime", "accident",
    "政治", "政府", "法律", "犯罪", "事故", "社会", "民生", "天气", "环境",
    # 教育 (非AI/数字化教育)
    "education", "school", "university", "student", "exam",
    "教育", "学校", "大学", "学生", "考试", "培训", "留学",
    # 其他非科技领域
    "agriculture", "farming", "pet", "travel", "hotel",
    "农业", "养殖", "宠物", "旅游", "酒店", "航空", "航空"
]


@dataclass
class CalibrationResult:
    """校准结果"""
    original_score: float           # 原始分数
    calibrated_score: float         # 校准后分数
    category: str                   # 分类
    category_confirmed: bool        # 分类是否确认
    is_related: bool                 # 是否相关
    reason: str                     # 校准理由
    action: str                     # 操作: pass, adjust, discard

    # 内容润色（新增）
    refined_title: str = ""         # 润色后的标题
    refined_summary: str = ""       # 润色后的摘要
    refined_content: str = ""       # 润色后的正文
    content_refined: bool = False   # 是否进行了内容润色


class NewsAICalibrator:
    """AI质量校准器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or MINIMAX_API_KEY
        self.enabled = bool(self.api_key)
    
    def calibrate(self, news_item: Dict) -> CalibrationResult:
        """对单条新闻进行AI校准"""
        if not self.enabled:
            # 无API时使用默认结果
            return CalibrationResult(
                original_score=news_item.get('quality', {}).get('total_100', 0),
                calibrated_score=news_item.get('quality', {}).get('total_100', 0),
                category=news_item.get('category', 'news'),
                category_confirmed=True,
                is_related=True,
                reason="AI校准未启用",
                action="pass"
            )

        # 构建校准提示词
        calibration_prompt = self._build_calibration_prompt(news_item)

        # 调用MiniMax API进行质量校准
        response = self._call_minimax(calibration_prompt)

        if response:
            result = self._parse_calibration_response(response, news_item)

            # 如果新闻通过审核且启用了内容润色，进行内容润色
            if result.action in ('pass', 'adjust') and self.enabled:
                refined = self._refine_content(news_item)
                if refined:
                    result.refined_title = refined.get('title', '')
                    result.refined_summary = refined.get('summary', '')
                    result.refined_content = refined.get('content', '')
                    result.content_refined = True

            return result
        else:
            # API失败时返回原始结果
            return CalibrationResult(
                original_score=news_item.get('quality', {}).get('total_100', 0),
                calibrated_score=news_item.get('quality', {}).get('total_100', 0),
                category=news_item.get('category', 'news'),
                category_confirmed=True,
                is_related=True,
                reason="API调用失败，保持原分数",
                action="pass"
            )

    def _refine_content(self, news: Dict, max_retries: int = 10) -> Optional[Dict]:
        """使用AI对新闻内容进行润色（带重试机制）

        润色目标:
        1. 标题简洁有力，15-30字
        2. 正文干净，删除无效信息
        3. 正文限制在150字以内，在句子边界截断

        注意: 不再输出摘要字段
        """
        title = news.get('title_zh') or news.get('title_en', '')
        content = news.get('content_zh') or news.get('content_en', '')

        refine_prompt = f"""你是一个专业的科技新闻编辑。请对以下新闻进行润色处理。

## 原始新闻
标题: {title}
正文: {content[:2000]}

## 润色要求
1. 标题: 简洁有力，15-30字，去除无关前缀后缀（如"36氪首发"、"爱范儿消息"等）
2. 正文: 删除以下无效信息:
   - "点击阅读全文"、"Read more"、"查看详情"等引导点击
   - "扫码关注"、"关注公众号"等引导关注
   - "图片来自于..."、"图源..."等图片来源说明
   - "责任编辑"、"作者"、"编辑"等署名信息
   - 重复的段落或句子
   - 广告内容
   - 过多的强调符号（如"！！！"）
   - HTML实体如&nbsp;等
3. 正文必须在句子边界（。！？）结束，字数不超过150字
4. 保持: 核心事实、数据、人名、公司名等重要信息不变

## 输出格式
请直接输出JSON，不要使用markdown格式:
{{
    "title": "润色后的标题",
    "content": "润色后的正文（在句子边界结束，最多150字）"
}}"""

        for attempt in range(max_retries):
            try:
                response = self._call_minimax(refine_prompt, max_tokens=1000)
                if response:
                    result = self._parse_refine_response(response)
                    if result and result.get('content'):
                        # 确保截断在句子边界
                        result['content'] = self._truncate_at_sentence(result['content'], 150)
                        # 检查是否在句子边界结束
                        if result['content'] and result['content'][-1] not in '。！？':
                            # 如果没有在句子边界结束，再尝试一次
                            if attempt < max_retries - 1:
                                print(f"      🔄 句子未完整，重试 ({attempt + 2}/{max_retries})...")
                                continue
                        return result
                    elif attempt < max_retries - 1:
                        print(f"      🔄 润色重试 ({attempt + 2}/{max_retries})...")
                        continue
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"      🔄 润色重试 ({attempt + 2}/{max_retries}): {e}")
                    continue
                print(f"   内容润色失败: {e}")

        return None

    def _truncate_at_sentence(self, text: str, max_length: int = 150) -> str:
        """在句子边界截断文本，确保不在词语中间截断"""
        if len(text) <= max_length:
            return text

        # 句子结束标记
        sentence_ends = ['。', '！', '？', '；', '\n']

        # 从max_length位置向前找最近的句子结束标记
        truncated = text[:max_length]
        last_end = -1

        for i, char in enumerate(truncated):
            if char in sentence_ends:
                last_end = i

        if last_end > max_length * 0.6:  # 如果句子结束位置在60%之后，使用它
            return truncated[:last_end + 1]

        # 否则向后找下一个句子结束标记
        remaining = text[max_length:]
        for i, char in enumerate(remaining):
            if char in sentence_ends:
                return text[:max_length + i + 1]

        # 没有找到句子边界，返回原始截断
        return truncated.rstrip()

    def _parse_refine_response(self, response: str) -> Optional[Dict]:
        """解析润色响应"""
        try:
            cleaned = response.strip()

            # 先移除 thinking 标签内容
            if '</think>' in cleaned:
                cleaned = cleaned.split('</think>')[-1].strip()

            # 提取JSON
            if '```json' in cleaned:
                cleaned = cleaned.split('```json')[1].split('```')[0]
            elif '```' in cleaned:
                cleaned = cleaned.split('```')[1]

            # 替换中文引号
            cleaned = cleaned.replace('"', '"').replace('"', '"')

            data = json.loads(cleaned.strip())

            # 强制限制长度
            refined_summary = data.get('summary', '')
            refined_content = data.get('content', '')

            # 摘要严格控制在80-100字
            if len(refined_summary) > 100:
                refined_summary = refined_summary[:100]
            elif len(refined_summary) < 80 and len(refined_summary) > 0:
                # 如果太短，至少保留可读性
                refined_summary = refined_summary[:100]

            # 正文限制在150字左右（但不在这里截断，由_truncate_at_sentence处理）
            if len(refined_content) > 150:
                refined_content = refined_content[:150]

            # 清理HTML实体
            refined_content = refined_content.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
            refined_title = data.get('title', '').replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')

            # 清理多余的空白
            refined_content = ' '.join(refined_content.split())
            refined_title = ' '.join(refined_title.split())

            return {
                'title': refined_title,
                'content': refined_content
            }
        except Exception as e:
            print(f"   解析润色结果失败: {e}")
            return None
    
    def _build_calibration_prompt(self, news: Dict) -> str:
        """构建校准提示词"""
        title = news.get('title_zh') or news.get('title_en', '')
        summary = news.get('summary_zh') or news.get('summary_en', '')
        source = news.get('source_zh') or news.get('source_en', '')
        original_score = news.get('quality', {}).get('total_100', 0)
        original_category = news.get('category', 'news')

        prompt = f"""评估新闻，只返回JSON，不能有其他文字。

标题: {title}
摘要: {summary[:200]}
来源: {source}
分数: {original_score}

我们只关注以下领域的新闻:
1. AI/人工智能: 大模型、机器学习、AI应用、ChatGPT、AIGC等
2. 开发工具: 编程框架、API服务、开发者平台、开源工具等
3. 数字产业动态: 数字化转型、数字经济、半导体、芯片、云计算、大数据、物联网、区块链、新能源汽车、自动驾驶等
4. 科技产品: 软件产品发布、设计创新等

过滤掉: 游戏/娱乐/影视/音乐/体育/财经(非科技)/医疗(非AI)/房产/零售/餐饮等

特别说明:
- "战略"类新闻必须有明确的数字化/科技内容才保留
- 只保留与数字产业、信息化、人工智能产业直接相关的新闻
- 财报新闻必须是科技公司(互联网/AI/半导体/新能源/运营商/设备商)

返回纯JSON:
{{"is_related":true,"category":"ai/tools/news/product之一","score_appropriate":true,"adjusted_score":{original_score},"reason":"理由","action":"pass"}}

只输出JSON，不要解释。"""

        return prompt
    
    # MiniMax API 配置
    API_BASE_URL = "https://api.minimaxi.com"

    # 支持的模型列表（按优先级）
    SUPPORTED_MODELS = [
        "MiniMax-M2.7",           # 最新模型，质量最好
        "MiniMax-M2.7-highspeed", # 快速版本
        "MiniMax-M2.5",           # 稳定版本
        "MiniMax-M2.5-highspeed", # 快速版本
    ]

    def _call_minimax(self, prompt: str, max_tokens: int = 500) -> Optional[Dict]:
        """调用 MiniMax API (OpenAI 兼容格式)"""
        try:
            url = f"{self.API_BASE_URL}/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # 尝试多个模型
            last_error = None
            for model in self.SUPPORTED_MODELS:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "你是一个专业的科技新闻质量评估专家。请严格按要求输出JSON格式。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,  # 低温度保证稳定性
                    "max_tokens": max_tokens
                }

                try:
                    response = requests.post(url, headers=headers, json=payload, timeout=60)
                    result = response.json()

                    # 检查成功
                    base_resp = result.get('base_resp', {})
                    if base_resp.get('status_code') == 0:
                        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                        return content

                    # 检查是否是模型不支持的错误
                    error_msg = base_resp.get('status_msg', '').lower()
                    if 'model' in error_msg and ('not' in error_msg or 'support' in error_msg or 'have' in error_msg):
                        last_error = f"模型 {model} 不支持"
                        continue  # 尝试下一个模型

                    # 其他错误
                    print(f"   MiniMax API错误: {error_msg}")
                    return None

                except Exception as e:
                    last_error = str(e)
                    continue

            # 所有模型都失败
            if last_error:
                print(f"   MiniMax API错误: {last_error}")
            return None

        except Exception as e:
            print(f"   API调用失败: {e}")
            return None
    
    def _parse_calibration_response(self, response: str, news: Dict) -> CalibrationResult:
        """解析API响应"""
        try:
            # 清理响应文本中的特殊字符
            cleaned = response.strip()

            # 提取JSON（处理可能的markdown格式和thinking内容）
            json_str = cleaned

            # 先移除 thinking 标签内容
            if '</think>' in json_str:
                json_str = json_str.split('</think>')[-1].strip()

            # 提取JSON（处理可能的markdown格式）
            if '```json' in json_str:
                json_str = json_str.split('```json')[1].split('```')[0]
            elif '```' in json_str:
                json_str = json_str.split('```')[1]

            # 替换中文引号为英文引号
            json_str = json_str.replace('"', '"').replace('"', '"')

            # 尝试直接解析
            try:
                data = json.loads(json_str.strip())
            except json.JSONDecodeError:
                # 如果失败，尝试提取部分JSON
                # 查找action字段
                import re
                action_match = re.search(r'"action"\s*:\s*"?(\w+)"?', json_str)
                category_match = re.search(r'"category"\s*:\s*"?(\w+)"?', json_str)
                is_related_match = re.search(r'"is_related"\s*:\s*(true|false)', json_str)
                adjusted_match = re.search(r'"adjusted_score"\s*:\s*(\d+\.?\d*)', json_str)

                if action_match:
                    data = {
                        'action': action_match.group(1),
                        'category': category_match.group(1) if category_match else news.get('category', 'news'),
                        'is_related': is_related_match.group(1) == 'true' if is_related_match else True,
                        'adjusted_score': float(adjusted_match.group(1)) if adjusted_match else news.get('quality', {}).get('total_100', 0)
                    }
                else:
                    raise ValueError("无法解析JSON响应")

            original_score = news.get('quality', {}).get('total_100', 0)
            action = data.get('action', 'pass')

            if action == 'discard':
                calibrated_score = 0
            elif action == 'adjust':
                calibrated_score = data.get('adjusted_score', original_score)
            else:
                calibrated_score = original_score

            # 标准化分类
            raw_category = data.get('category', news.get('category', 'news'))
            CATEGORY_MAP = {
                'ai': 'ai', 'tool': 'tools', 'tools': 'tools',
                'news': 'news', '动态': 'news', 'digital': 'news', 'digital_industry': 'news',
                'product': 'product', '产品': 'product', '科技产品': 'product'
            }
            category = CATEGORY_MAP.get(raw_category, raw_category)
            # 如果不在有效分类中，设为 news
            if category not in ('ai', 'tools', 'news', 'product'):
                category = 'news'

            return CalibrationResult(
                original_score=original_score,
                calibrated_score=calibrated_score,
                category=category,
                category_confirmed=data.get('category_confirmed', True),
                is_related=data.get('is_related', True),
                reason=data.get('reason', ''),
                action=action
            )

        except Exception as e:
            # 解析失败时返回原始结果
            return CalibrationResult(
                original_score=news.get('quality', {}).get('total_100', 0),
                calibrated_score=news.get('quality', {}).get('total_100', 0),
                category=news.get('category', 'news'),
                category_confirmed=True,
                is_related=True,
                reason="解析失败，保持原分数",
                action="pass"
            )
    
    def batch_calibrate(self, news_list: List[Dict],
                        min_score: int = 50) -> Tuple[List[Dict], Dict]:
        """批量校准新闻

        Returns:
            (保留的新闻列表, 统计信息)
        """
        if not self.enabled:
            # 未启用AI校准，只过滤低分
            filtered = [n for n in news_list
                       if n.get('quality', {}).get('total_100', 0) >= min_score]
            return filtered, {"total": len(news_list), "passed": len(filtered),
                            "ai_calibration": "disabled"}

        print(f"\n[AI校准] 开始校准 {len(news_list)} 条新闻...")

        results = []
        stats = {
            "total": len(news_list),
            "passed": 0,
            "adjusted": 0,
            "discarded": 0,
            "content_refined": 0,
            "categories": {"ai": 0, "tools": 0, "news": 0, "product": 0, "other": 0}
        }

        for i, news in enumerate(news_list):
            print(f"   [{i+1}/{len(news_list)}] {news.get('title_zh', '')[:30]}...")

            result = self.calibrate(news)

            # 应用校准结果
            if result.action == 'discard' or not result.is_related:
                stats["discarded"] += 1
                print(f"      ❌ 舍弃: {result.reason}")
                continue

            # 更新分数和分类
            if result.action == 'adjust':
                stats["adjusted"] += 1
                news['quality']['total_100'] = result.calibrated_score
                news['quality']['ai_calibrated'] = True
                news['quality']['calibration_reason'] = result.reason
                print(f"      🔄 修正分数: {result.original_score} → {result.calibrated_score}")

            if result.category_confirmed and result.category != news.get('category'):
                news['category'] = result.category
                news['category_confirmed'] = True
                print(f"      📁 分类修正: → {result.category}")

            # 应用内容润色
            if result.content_refined:
                stats["content_refined"] += 1
                if result.refined_title:
                    news['title_zh'] = result.refined_title
                if result.refined_content:
                    # 使用润色后的内容（已在_truncate_at_sentence处理）
                    news['content_zh'] = result.refined_content
                news['quality']['content_refined'] = True
                print(f"      ✨ 内容润色完成 ({len(result.refined_content)}字)")
            else:
                # 如果没有润色，确保正文在150字以内并在句子边界截断
                content = news.get('content_zh', '')
                if len(content) > 150:
                    # 使用句子边界截断
                    truncator = self._truncate_at_sentence(content, 150)
                    news['content_zh'] = truncator
                    print(f"      📝 内容简化 ({len(content)}→{len(truncator)}字)")
                # 清理HTML实体
                news['content_zh'] = news['content_zh'].replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
                news['content_zh'] = ' '.join(news['content_zh'].split())

            # 更新等级
            score = news['quality']['total_100']
            if score >= 85: news['quality']['grade'] = 'A+'
            elif score >= 75: news['quality']['grade'] = 'A'
            elif score >= 65: news['quality']['grade'] = 'B'
            elif score >= 55: news['quality']['grade'] = 'C'
            else: news['quality']['grade'] = 'D'

            results.append(news)
            stats["passed"] += 1
            stats["categories"][result.category] = stats["categories"].get(result.category, 0) + 1

        print(f"\n[AI校准完成] 通过: {stats['passed']}, 修正: {stats['adjusted']}, 润色: {stats['content_refined']}, 舍弃: {stats['discarded']}")

        return results, stats


# 全局实例
calibrator = NewsAICalibrator()
