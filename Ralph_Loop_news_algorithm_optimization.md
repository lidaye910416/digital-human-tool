# Ralph Loop: 新闻质量控制算法优化

## 目标
在**不删减AI处理流程**的前提下，优化MiniMax API调用逻辑，减少冗余调用，同时确保输出质量满足要求：
- 正文 150 字左右
- 内容简洁精炼
- 良好分类
- 过滤无关内容

## 当前问题分析

### 1. 当前API调用流程
```
每条新闻 → calibrate() → 2次API调用
                        ├── 调用1: _build_calibration_prompt (分类验证/领域判断)
                        └── 调用2: _refine_content (内容润色)
```

### 2. 冗余点
1. **两次独立调用**：calibrate 和 refine_content 是分开调用的
2. **prompt 重复**：两次调用都包含 title/summary/source 信息
3. **解析逻辑重复**：每次都需要解析 JSON，处理 thinking 标签

### 3. 优化方向

#### 方案A: 合并为单次调用
- 一次调用同时完成：分类验证 + 领域判断 + 内容润色
- 风险：prompt 可能过长，导致输出不稳定

#### 方案B: 优化 prompt 和解析逻辑
- 精简 prompt，减少 token 消耗
- 优化 JSON 解析，减少解析失败
- 添加更好的缓存/重试机制

#### 方案C: 智能重试策略
- 首次调用失败才重试
- 根据错误类型决定重试次数
- 合并小批次处理减少 API 调用次数

## 任务清单

- [ ] 分析 test/raw_collection/ 中的测试数据
- [ ] 设计合并后的 prompt 模板
- [ ] 实现单次调用完成分类+润色的逻辑
- [ ] 优化 JSON 解析和错误处理
- [ ] 测试优化后的算法
- [ ] 对比优化前后的 API 调用次数和质量

## 测试数据位置
- `test/raw_collection/raw_news.json` - 110条原始数据
- `test/raw_collection/high_quality_news.json` - 20条高分数据(≥55分)

## 输出目标
```json
{
  "id": "uuid",
  "title_zh": "AI润色后的标题 (15-30字)",
  "content_zh": "AI润色后的正文 (≤150字, 句子边界结束)",
  "category": "ai/tools/news/product",
  "quality": { "total_100": xx, "grade": "C" }
}
```
