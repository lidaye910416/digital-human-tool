"""
TechEcho Pro - AI质量校准器

功能:
1. 基于规则评分结果，使用AI进行二次校准
2. 分类验证与修正
3. 过滤无关内容（如游戏、娱乐）
4. 自动修正明显错误的分数

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
                    "机器学习", "自然语言处理", "计算机视觉", "AI应用", "AI工具", "AI产品"]
    },
    "tools": {
        "name": "开发工具",
        "description": "前沿科技工具、开发框架、API服务",
        "keywords": ["GitHub", "VS Code", "API", "SDK", "框架", "Python", "JavaScript", "Rust",
                    "编程", "开发", "开源", "代码", "IDE", "编译器", "Docker", "Kubernetes",
                    "Git", "数据库", "云服务", "AWS", "Azure", "GCP", "Vercel", "Netlify"]
    },
    "news": {
        "name": "科技动态",
        "description": "数字产业、产业数字化动态",
        "keywords": ["发布", "收购", "融资", "裁员", "上市", "合作", "投资", "财报", "业绩",
                    "战略", "转型", "布局", "数字经济", "产业数字化", "数字化转型",
                    "科技公司", "互联网", "半导体", "芯片", "新能源", "电动汽车"]
    },
    "product": {
        "name": "产品设计",
        "description": "优秀软件产品、设计创新",
        "keywords": ["产品", "设计", "UI", "UX", "App", "Launch", "发布", "更新", "版本",
                    "软件", "应用", "小程序", "网站", "平台", "功能", "界面", "交互",
                    "苹果", "谷歌", "微软", "Meta", "产品发布", "新功能"]
    }
}

# 过滤无关分类
UNRELATED_CATEGORIES = [
    "game", "gaming", "entertainment", "movie", "music", "sports",
    "游戏", "娱乐", "电影", "音乐", "体育", "八卦", "明星"
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
        
        # 构建提示词
        prompt = self._build_prompt(news_item)
        
        # 调用MiniMax API
        response = self._call_minimax(prompt)
        
        if response:
            return self._parse_response(response, news_item)
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
    
    def _build_prompt(self, news: Dict) -> str:
        """构建校准提示词"""
        title = news.get('title_zh') or news.get('title_en', '')
        summary = news.get('summary_zh') or news.get('summary_en', '')
        content = (news.get('content_zh') or news.get('content_en', ''))[:500]
        source = news.get('source_zh') or news.get('source_en', '')
        original_score = news.get('quality', {}).get('total_100', 0)
        original_category = news.get('category', 'news')
        original_scores = news.get('quality', {}).get('scores', {})
        
        prompt = f"""你是一个专业的科技新闻质量评估专家。请对以下新闻进行AI二次校准。

## 新闻信息
标题: {title}
摘要: {summary}
正文: {content}
来源: {source}
原始分数: {original_score}
原始分类: {original_category}

## 规则评分详情
- completeness: {original_scores.get('completeness', 0)} (内容完整性)
- language: {original_scores.get('language', 0)} (语言质量)
- title: {original_scores.get('title', 0)} (标题质量)
- source_credibility: {original_scores.get('source_credibility', 0)} (来源权威性)
- info_density: {original_scores.get('info_density', 0)} (信息密度)
- actionability: {original_scores.get('actionability', 0)} (可操作性)
- impact: {original_scores.get('impact', 0)} (影响力)
- originality: {original_scores.get('originality', 0)} (独创性)

## 四大目标分类
1. AI: AI基础能力、大模型、机器学习相关
2. tools: 前沿科技工具、开发框架、API服务
3. news: 数字产业、产业数字化动态
4. product: 优秀软件产品、设计创新

## 过滤条件
以下内容应被舍弃:
- 游戏、电竞相关
- 娱乐八卦
- 音乐、影视
- 体育赛事

## 任务
1. 判断新闻是否属于四大目标分类（是/否）
2. 评估原始分数是否合理
3. 如果分数明显不合理，给出修正建议
4. 决定操作：pass（通过）、adjust（修正分数后通过）、discard（舍弃）

请以JSON格式返回结果:
{{
    "is_related": true/false,  // 是否属于四大分类
    "category": "ai/tools/news/product",  // 确认的分类
    "category_confirmed": true/false,  // 分类是否需要修正
    "score_appropriate": true/false,  // 原始分数是否合理
    "adjusted_score": 75.0,  // 如果分数不合理，修正后的分数(0-100)
    "reason": "校准理由",  // 简短说明
    "action": "pass/adjust/discard"  // 操作建议
}}"""
        
        return prompt
    
    def _call_minimax(self, prompt: str) -> Optional[Dict]:
        """调用MiniMax API"""
        try:
            url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "MiniMax-M2.7",  # 使用最新的 M2.7 模型
                "messages": [
                    {"role": "system", "content": "你是一个专业的科技新闻质量评估专家。请严格按要求输出JSON格式。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,  # 低温度保证稳定性
                "max_tokens": 500
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                # 检查API返回的错误
                base_resp = result.get('base_resp', {})
                if base_resp.get('status_code') == 0:
                    content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                    return content
                else:
                    error_msg = base_resp.get('status_msg', 'Unknown error')
                    print(f"   MiniMax API错误: {error_msg}")
                    return None
            else:
                print(f"   MiniMax HTTP错误: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   API调用失败: {e}")
            return None
    
    def _parse_response(self, response: str, news: Dict) -> CalibrationResult:
        """解析API响应"""
        try:
            # 清理响应文本中的特殊字符
            cleaned = response.strip()

            # 提取JSON（处理可能的markdown格式）
            json_str = cleaned
            if '```json' in cleaned:
                json_str = cleaned.split('```json')[1].split('```')[0]
            elif '```' in cleaned:
                json_str = cleaned.split('```')[1]

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

            return CalibrationResult(
                original_score=original_score,
                calibrated_score=calibrated_score,
                category=data.get('category', news.get('category', 'news')),
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
        
        print(f"\n[AI校准完成] 通过: {stats['passed']}, 修正: {stats['adjusted']}, 舍弃: {stats['discarded']}")
        
        return results, stats


# 全局实例
calibrator = NewsAICalibrator()
