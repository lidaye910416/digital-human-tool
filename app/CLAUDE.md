# TechEcho Pro - 科技回声

## 项目概览
科技新闻聚合与语音播报平台，支持中英双语，提供4种语音朗读风格。

## 新闻收集与处理流程

```
┌─────────────────────────────────────────────────────────────┐
│  1. 收集新闻 (RSS feeds)                                    │
│  2. 规则评分 (8维度质量分析)                                 │
│  3. AI校准 (MiniMax 2.7)                                    │
│     - 验证分类(AI/tools/news/product)                       │
│     - 修正不合理分数                                         │
│     - 过滤无关内容(游戏/娱乐)                                │
│  4. 生成TTS (4种语音风格)                                   │
│  5. 保存到数据库                                             │
└─────────────────────────────────────────────────────────────┘
```

## 数据结构 (重要 - 不可修改)

### news.json 顶层结构
```json
{
  "lastUpdate": "YYYY-MM-DD HH:MM",
  "totalCount": 31,
  "stats": {
    "A+": 0,
    "A": 0,
    "B": 5,
    "C": 15,
    "D": 11
  },
  "categories": {
    "ai": 10,
    "tools": 5,
    "news": 12,
    "product": 4
  },
  "news": [...]
}
```

### 单条新闻数据结构
```json
{
  "id": "UUID格式唯一标识",
  "title_zh": "中文标题",
  "title_en": "英文标题",
  "summary_zh": "中文摘要",
  "summary_en": "英文摘要",
  "content_zh": "中文正文",
  "content_en": "英文正文",
  "source_zh": "中文来源",
  "source_en": "英文来源",
  "source_url": "https://... (原文链接，前端可点击跳转)",
  "lang": "zh | en | bilingual",
  "category": "ai | tools | news | product",
  "published_at": "YYYY-MM-DD HH:MM:SS  +0800",
  "created_at": "ISO格式时间戳",
  "quality": {
    "total_100": 70.0,
    "grade": "A+ | A | B | C | D",
    "scores": {
      "completeness": 7.5,
      "language": 8.0,
      "title": 7.0,
      "source_credibility": 9.0,
      "info_density": 10,
      "actionability": 5.0,
      "impact": 5.5,
      "originality": 5.0
    },
    "ai_calibrated": true,      // 可选，AI校准后添加
    "calibration_reason": "..."  // 可选，AI校准理由
  },
  "audio": {
    "voice1": "/data/audio/{hash}.mp3",
    "voice2": "/data/audio/{hash}.mp3",
    "voice3": "/data/audio/{hash}.mp3",
    "voice4": "/data/audio/{hash}.mp3"
  }
}
```

### 四大分类
- **ai**: AI人工智能、大模型、机器学习
- **tools**: 开发工具、框架、API服务
- **news**: 科技动态、融资、收购、财报
- **product**: 优秀软件产品、设计创新

### 关键字段说明
- **id**: 新闻唯一ID，用于生成音频缓存key
- **source_url**: 原文链接，前端显示为可点击链接
- **lang**: `zh`(中文)、`en`(英文)、`bilingual`(双语)
- **category**: 必须是 `ai`|`tools`|`news`|`product` 之一
- **audio**: 包含4种语音风格的文件路径，key为 `voice1`-`voice4`
  - voice1: 晓晓-女声 (zh-CN-XiaoxiaoNeural)
  - voice2: 云希-男声 (zh-CN-YunxiNeural)
  - voice3: 晓伊-女声 (zh-CN-XiaoyiNeural)
  - voice4: 云扬-男声 (zh-CN-YunyangNeural)

### 前端期望的字段
- `id`: 必需
- `title_zh` / `title_en`: 根据当前语言显示
- `summary_zh` / `summary_en`: 新闻卡片摘要
- `content_zh` / `content_en`: 详情页内容
- `source_zh` / `source_en`: 来源显示
- `source_url`: 原文链接(可点击)
- `lang`: 过滤语言
- `category`: 分类过滤
- `published_at`: 日期显示
- `quality.total_100`: 分数阈值过滤
- `audio`: TTS播放，key为 voice1-voice4

## 技术栈
- **前端**: 原生HTML/JS (app/index.html) 或 Taro
- **后端**: Python (src/services/)
- **AI校准**: MiniMax 2.7 模型
- **新闻源**: RSS feeds (钛媒体/爱范儿/少数派/36氪等)
- **TTS**: edge-tts (兜底) / MiniMax TTS (优先)
- **存储**: app/data/news.json, app/data/audio/*.mp3

## 目录结构
```
digital-human-tool/
├── app/
│   ├── index.html          # 前端主文件
│   ├── CLAUDE.md           # 本文档
│   └── data/
│       ├── news.json       # 新闻数据
│       └── audio/          # TTS音频文件
├── scripts/
│   ├── news_workflow.py    # 新闻收集+TTS生成工作流
│   └── daily_workflow.sh   # 定时任务脚本
├── src/
│   ├── models/             # 数据模型
│   │   └── news_bilingual.py
│   └── services/
│       ├── news_collector_v2.py  # 新闻收集器
│       └── news_ai_calibrator.py # AI校准器
└── ralph/
    └── prd.json            # 产品需求文档
```

## 常用命令
```bash
# 运行完整工作流（收集 + AI校准 + TTS）
PYTHONPATH=. python3 scripts/news_workflow.py --min-quality 50

# 只收集新闻，跳过TTS
PYTHONPATH=. python3 scripts/news_workflow.py --skip-tts

# 跳过AI校准（使用规则评分）
PYTHONPATH=. python3 scripts/news_workflow.py --skip-ai

# 本地开发服务器
cd app && python3 -m http.server 8080
```

## 自动化任务
```bash
# 查看定时任务
crontab -l

# 手动运行每日工作流
./scripts/daily_workflow.sh

# 查看执行日志
cat logs/workflow_20260428.log
```

### 定时任务配置
- **执行时间**: 每天早上 7:00
- **任务脚本**: `scripts/daily_workflow.sh`
- **日志目录**: `logs/`
- **工作流**: 收集 → 规则评分 → AI校准 → TTS生成 → 保存

## 注意事项
1. **数据结构稳定性**: news.json 结构必须保持向后兼容
2. **audio字段**: 即使没有生成TTS，也要保留空对象 `{}`
3. **lang字段**: 必须使用 `zh`、`en`、`bilingual` 三个值之一
4. **category字段**: 必须使用 `ai`、`tools`、`news`、`product` 四个值之一
5. **quality字段**: 后端计算，前端用于阈值过滤显示
6. **audio路径**: 使用 `/data/audio/` 前缀，前端会拼接完整URL
7. **source_url字段**: 原文链接，前端显示为可点击链接
