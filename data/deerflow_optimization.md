# DeerFlow 新闻质量分析优化建议

生成时间: 2026-04-28T09:40:43.979328

# 新闻质量评分系统优化方案

## 一、新评分维度体系

| 维度 | 权重 | 说明 |
|------|------|------|
| 内容完整性 | 15% | 摘要是否涵盖核心信息 |
| 语言质量 | 15% | 翻译流畅度与可读性 |
| 标题质量 | 10% | 标题清晰度与吸引力 |
| 来源权威性 | 10% | 来源的可靠性和专业性 |
| 信息密度 | 10% | 单位字数的信息量 |
| **可操作性** | 15% | 读者能否获得可执行的洞察 |
| **影响力** | 15% | 新闻的重要性与时效性 |
| **独创性** | 10% | 是否有独特视角或分析 |

---

## 二、各维度评分规则详解

### 1. 可操作性 (Actionability) — 0~10分

**核心问题**：读者读完这篇新闻，能做什么？

| 等级 | 分数 | 特征 |
|------|------|------|
| 高 | 8-10 | 明确指导行动（如：投资建议、购买时机、技术选型） |
| 中 | 5-7 | 提供决策框架，但需读者自行判断 |
| 低 | 2-4 | 仅有事实陈述，无行动指引 |
| 差 | 0-1 | 标题党或纯情绪煽动 |

**评分要素**：
- 是否包含具体数据/时间节点
- 是否有明确的受众定位（谁该采取行动）
- 是否提供备选方案或风险提示

---

### 2. 影响力 (Impact) — 0~10分

**核心问题**：这篇新闻有多重要？

| 等级 | 分数 | 特征 |
|------|------|------|
| 高 | 8-10 | 改变行业格局、重大政策、突破性技术 |
| 中 | 5-7 | 影响特定群体、有实质性进展 |
| 低 | 2-4 | 一般性事件、常规更新 |
| 差 | 0-1 | 无实质内容的软新闻 |

**评分要素**：
- 时效性（发生时间 vs 发布时间）
- 涉及人数/金额规模
- 是否是"首次"/"最大"/"最小"
- 是否有后续跟踪价值

---

### 3. 独创性 (Originality) — 0~10分

**核心问题**：这篇新闻提供了什么独特价值？

| 等级 | 分数 | 特征 |
|------|------|------|
| 高 | 8-10 | 独家报道、原创分析、深度解读 |
| 中 | 5-7 | 综合多方来源、添加背景信息 |
| 低 | 2-4 | 简单编译、缺乏增值内容 |
| 差 | 0-1 | 完全复制、无任何增量 |

**评分要素**：
- 是否有多源交叉验证
- 是否提供历史对比或趋势分析
- 是否有专家解读或独家观点
- 是否揭示事件背后的原因

---

### 4. 语言质量 (Language Quality) — 0~10分

**升级版评分规则**（替代原来的"中文字符比例"）：

```python
def evaluate_language_quality(text: str) -> float:
    """
    多维度评估语言质量
    """
    scores = []
    
    # 1. 流畅度检查 (30%)
    #    - 检测翻译腔句式（的、地、得滥用）
    #    - 检测句子长度是否合理（中文20-40字为佳）
    fluency_score = analyze_fluency(text)  # 0-10
    
    # 2. 专业术语准确性 (30%)
    #    - 检测领域专有名词是否正确使用
    #    - 检测缩写是否首次出现时解释
    terminology_score = check_terminology(text)  # 0-10
    
    # 3. 可读性指数 (20%)
    #    - 使用结巴分词计算句子长度分布
    #    - 避免过于书面化或过于口语化
    readability_score = calculate_readability(text)  # 0-10
    
    # 4. 标点与格式规范 (20%)
    #    - 标点使用是否规范
    #    - 数字、英文、汉字混排是否合理
    format_score = check_formatting(text)  # 0-10
    
    # 加权平均
    final_score = (
        fluency_score * 0.3 +
        terminology_score * 0.3 +
        readability_score * 0.2 +
        format_score * 0.2
    )
    
    return final_score
```

---

### 5. 来源权威性 (Source Credibility) — 0~10分

```python
def evaluate_source_credibility(source: str, url: str) -> float:
    """
    多层级评估来源权威性
    """
    score = 5.0  # 默认中等
    
    # 1. 媒体级别加成
    tier1_media = ["新华社", "人民日报", "BBC", "Reuters", "AP", "NYT"]
    tier2_media = ["财经网", "36kr", "TechCrunch", "The Verge"]
    
    if any(media in source for media in tier1_media):
        score += 3.0
    elif any(media in source for media in tier2_media):
        score += 1.5
    
    # 2. 域名信誉
    gov_domains = [".gov.cn", ".org", ".edu"]
    if any(domain in url for domain in gov_domains):
        score += 1.0
    
    # 3. 学术来源
    if "arxiv.org" in url or "doi.org" in url:
        score += 2.0
    
    # 4. 自媒体惩罚
    personal_domains = ["weibo.com", "mp.weixin.qq.com", "toutiao.com"]
    if any(domain in url for domain in personal_domains):
        score -= 2.0
    
    return max(0, min(10, score))  # 限制在0-10
```

---

### 6. 内容完整性 (Completeness) — 0~10分

```python
REQUIRED_ELEMENTS = {
    "who": "事件主体（人物/机构）",
    "what": "核心事件/结论",
    "when": "时间节点",
    "where": "地点/语境",
    "why": "原因/背景",
    "how": "方式/过程"
}

def evaluate_completeness(text: str) -> float:
    """
    评估5W1H要素覆盖情况
    """
    present_elements = 0
    
    for element_key, description in REQUIRED_ELEMENTS.items():
        if check_element_presence(text, element_key):
            present_elements += 1
    
    # 基础分：每个要素占1.5分，满分9分
    base_score = present_elements * 1.5
    
    # 加分项：是否有引用、数据、来源标注
    bonus = 0
    if has_citations(text): bonus += 0.5
    if has_data_or_statistics(text): bonus += 0.5
    
    return min(10, base_score + bonus)
```

---

## 三、综合质量分数计算公式

### 加权总分模型

```
Quality_Score = Σ(维度分数 × 权重)
```

**Python 实现**：

```python
def calculate_news_quality_score(article: dict) -> dict:
    """
    计算新闻综合质量分数
    
    Args:
        article: 包含以下字段的字典
            - title: 标题
            - content: 正文
            - source: 来源
            - url: 链接
            - publish_date: 发布时间
    
    Returns:
        包含各维度分数和总分的字典
    """
    
    # 维度权重配置
    WEIGHTS = {
        "completeness": 0.15,      # 内容完整性
        "language": 0.15,          # 语言质量
        "title": 0.10,             # 标题质量
        "source_credibility": 0.10, # 来源权威性
        "info_density": 0.10,       # 信息密度
        "actionability": 0.15,      # 可操作性
        "impact": 0.15,             # 影响力
        "originality": 0.10         # 独创性
    }
    
    # 计算各维度分数
    scores = {
        "completeness": evaluate_completeness(article["content"]),
        "language": evaluate_language_quality(article["content"]),
        "title": evaluate_title_quality(article["title"], article["content"]),
        "source_credibility": evaluate_source_credibility(
            article["source"], 
            article["url"]
        ),
        "info_density": evaluate_info_density(article["content"]),
        "actionability": evaluate_actionability(article["content"]),
        "impact": evaluate_impact(article, WEIGHTS),
        "originality": evaluate_originality(article)
    }
    
    # 计算加权总分（满分10分）
    weighted_sum = sum(
        scores[dimension] * WEIGHTS[dimension] 
        for dimension in WEIGHTS
    )
    
    # 转换为百分制，便于理解
    total_score_100 = weighted_sum * 10
    
    # 质量等级判定
    if total_score_100 >= 85:
        grade = "A+ (卓越)"
    elif total_score_100 >= 75:
        grade = "A (优秀)"
    elif total_score_100 >= 65:
        grade = "B (良好)"
    elif total_score_100 >= 55:
        grade = "C (一般)"
    else:
        grade = "D (较差)"
    
    return {
        "dimensions": scores,
        "weighted_total": round(weighted_sum, 2),
        "total_100": round(total_score_100, 1),
        "grade": grade,
        "weights_used": WEIGHTS
    }
```

---

## 四、质量等级参考标准

| 等级 | 分数区间 | 含义 | 建议 |
|------|----------|------|------|
| A+ | 85-100 | 卓越报道 | 优先推荐 |
| A | 75-84 | 优秀报道 | 值得阅读 |
| B | 65-74 | 良好报道 | 可作参考 |
| C | 55-64 | 一般报道 | 需补充信息 |
| D | <55 | 较差报道 | 不建议采用 |

---

## 五、实施建议

### 第一阶段：基础实现
- 先实现基于规则的评分（关键词、正则表达式）
- 建立评分样本库用于验证

### 第二阶段：模型增强
- 引入 NLP 模型判断语义完整性
- 使用情感分析检测标题党倾向

### 第三阶段：持续优化
- 建立用户反馈机制
- A/B 测试不同权重配置
- 定期用人工标注数据校准模型

---

是否需要我为某个具体维度提供更详细的实现代码？新闻质量评分系统优化