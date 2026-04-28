# TechEcho Pro - 智能科技资讯平台

> **版本**: v0.3.0  
> **分支**: `feature/techecho-redesign`  
> **更新日期**: 2026-04-28

---

## 🎯 产品概述

**TechEcho Pro** - 智能科技资讯平台
- 多源收集科技资讯，自动质量评分与分类
- 支持日期筛选、信息源切换（中英文）
- TTS 语音朗读 + 数字人视频播报（开发中）
- 多端支持：微信小程序、Web、桌面端

**核心价值**: 为用户提供经过 AI 筛选、分级、分类的高质量科技资讯

---

## 📋 功能清单

### 核心功能 (P0)

| 功能 | 描述 | 状态 |
|------|------|------|
| 日期切换 | 滚轮式日期选择，查看特定日期资讯 | ⏳ 开发中 |
| 分类浏览 | 优雅的分类标签切换，LLM 智能分类 | ⏳ 开发中 |
| 语言切换 | 中英文资讯筛选与双语展示 | ✅ 已完成 |
| 质量过滤 | 自动过滤评分过低的资讯（< 55分） | ⏳ 开发中 |
| 资讯卡片 | 展示标题、摘要、来源、评分 | ⏳ 优化中 |
| TTS 朗读 | 一键语音朗读资讯内容 | ⏳ 开发中 |
| 数字人播报 | 数字人视频朗读（预留） | 🔜 待完善 |

### 交互优化 (P1)

| 功能 | 描述 |
|------|------|
| 日期滚轮动画 | 拟人化、流畅的日期切换动效 |
| 分类切换动画 | 标签滑动 + 内容渐变动效 |
| 下拉刷新 | 下拉获取最新资讯 |
| 卡片展开 | 点击展开完整内容 |

---

## 🎨 设计规范

### 设计参考
- **UI 组件库**: [shadcn/ui](https://github.com/shadcn-ui/ui)
- **设计风格**: 极简主义 + 玻璃拟态 + 微妙动效
- **色彩系统**: 深色主题 + 渐变强调色

### 色彩系统

```css
:root {
  /* 背景色 */
  --bg-primary: #09090b;      /* 主背景 - 近乎纯黑 */
  --bg-secondary: #18181b;    /* 次级背景 */
  --bg-card: #27272a;         /* 卡片背景 */
  --bg-elevated: #3f3f46;     /* 悬浮/强调背景 */
  
  /* 文字色 */
  --text-primary: #fafafa;    /* 主文字 - 纯白 */
  --text-secondary: #a1a1aa;  /* 次文字 - 灰 */
  --text-muted: #71717a;      /* 弱化文字 */
  
  /* 强调色 */
  --accent-primary: #6366f1;   /* 主强调 - 靛蓝 */
  --accent-secondary: #8b5cf6; /* 次强调 - 紫色 */
  --accent-glow: rgba(99, 102, 241, 0.4); /* 发光效果 */
  
  /* 语义色 */
  --success: #22c55e;         /* 成功/高质量 */
  --warning: #f59e0b;         /* 警告/中质量 */
  --danger: #ef4444;          /* 危险/低质量 */
  
  /* 渐变 */
  --gradient-primary: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  --gradient-accent: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
}
```

### 字体系统

```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* 字号 */
--text-xs: 0.75rem;    /* 12px - 辅助文字 */
--text-sm: 0.875rem;   /* 14px - 次要文字 */
--text-base: 1rem;     /* 16px - 正文 */
--text-lg: 1.125rem;   /* 18px - 标题 */
--text-xl: 1.25rem;    /* 20px - 大标题 */
--text-2xl: 1.5rem;    /* 24px - 页面标题 */
```

### 间距系统

```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
```

### 圆角系统

```css
--radius-sm: 0.375rem;  /* 6px - 小圆角 */
--radius-md: 0.5rem;     /* 8px - 中圆角 */
--radius-lg: 0.75rem;    /* 12px - 大圆角 */
--radius-xl: 1rem;       /* 16px - 超大圆角 */
--radius-full: 9999px;  /* 圆形 */
```

### 阴影系统

```css
--shadow-sm: 0 1px 2px rgba(0,0,0,0.5);
--shadow-md: 0 4px 6px rgba(0,0,0,0.4);
--shadow-lg: 0 10px 15px rgba(0,0,0,0.3);
--shadow-glow: 0 0 20px var(--accent-glow);
```

### 动效规范

```css
/* 缓动函数 */
--ease-out: cubic-bezier(0.16, 1, 0.3, 1);
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);

/* 时长 */
--duration-fast: 150ms;
--duration-normal: 250ms;
--duration-slow: 400ms;
--duration-slower: 600ms;
```

---

## 🗂️ 页面结构

### 首页布局

```
┌─────────────────────────────────────┐
│  Header (固定)                       │
│  ┌─────────────────────────────────┐ │
│  │ Logo    日期选择  语言切换       │ │
│  └─────────────────────────────────┘ │
├─────────────────────────────────────┤
│  分类标签栏 (横向滚动)               │
│  [推荐] [AI] [工具] [产品] [动态]   │
├─────────────────────────────────────┤
│  资讯列表 (可刷新)                   │
│  ┌─────────────────────────────────┐ │
│  │ Card 1                          │ │
│  │   📰 标题                        │ │
│  │   来源 · 日期 · 评分 Badge       │ │
│  │   📖 阅读  🔊 朗读  🎬 播报      │ │
│  └─────────────────────────────────┘ │
│  ┌─────────────────────────────────┐ │
│  │ Card 2                          │ │
│  └─────────────────────────────────┘ │
│  ...                                 │
├─────────────────────────────────────┤
│  底部导航 (固定)                     │
│  [首页] [收藏] [我的]               │
└─────────────────────────────────────┘
```

### 关键组件

#### 1. 日期选择器
- **类型**: 滚轮式日期选择器
- **位置**: Header 右侧，点击图标展开
- **动画**: 从顶部滑入 + 背景模糊遮罩
- **交互**: 上下滑动选择日期，支持快捷按钮（今天、昨天）

#### 2. 分类标签栏
- **类型**: 横向滚动的标签列表
- **位置**: Header 下方
- **动画**: 标签切换时内容渐变过渡
- **交互**: 点击标签高亮选中，支持滑动切换

#### 3. 资讯卡片
- **布局**: 标题 + 摘要 + 元信息 + 操作按钮
- **状态**: 默认、展开、朗读中
- **动画**: 点击展开时高度平滑过渡

#### 4. 底部导航
- **项目**: 首页、收藏、我的
- **样式**: 图标 + 文字，选中态高亮

---

## 🔧 技术方案

### 多端架构

```
┌─────────────────────────────────────────┐
│              业务逻辑层 (Shared)          │
│  ┌─────────────────────────────────────┐ │
│  │ NewsService · QualityService        │ │
│  │ TTSService · CategoryService        │ │
│  └─────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│              数据层 (Shared)              │
│  ┌─────────────────────────────────────┐ │
│  │ SQLite + JSON (本地存储)            │ │
│  │ API Client (远程同步)               │ │
│  └─────────────────────────────────────┘ │
├──────────────────┬──────────────────────┤
│   小程序端        │   Web 端             │
│  ┌─────────────┐ │  ┌─────────────────┐  │
│  │ Taro       │ │  │ React + Vite   │  │
│  │ (WeChat)   │ │  │ shadcn/ui      │  │
│  └─────────────┘ │  └─────────────────┘  │
└──────────────────┴──────────────────────┘
```

### 目录结构

```
tech-echo-pro/
├── src/                      # 后端 Python 代码
│   ├── services/             # 业务服务
│   │   ├── news_collector.py # 资讯收集
│   │   ├── quality_analyzer.py # 质量分析
│   │   ├── category_analyzer.py # LLM 分类
│   │   └── tts_service.py   # TTS 服务
│   ├── models/               # 数据模型
│   └── api/                  # API 路由
│
├── app/                      # 前端应用 (Taro 多端)
│   ├── src/
│   │   ├── components/       # 通用组件
│   │   │   ├── DatePicker/   # 日期选择器
│   │   │   ├── CategoryTabs/ # 分类标签
│   │   │   ├── NewsCard/     # 资讯卡片
│   │   │   └── AudioPlayer/  # 音频播放器
│   │   ├── pages/
│   │   │   ├── index/       # 首页
│   │   │   ├── collection/   # 收藏
│   │   │   └── profile/      # 我的
│   │   ├── hooks/           # 自定义 Hooks
│   │   ├── services/        # API 调用
│   │   └── stores/          # 状态管理
│   └── config/              # Taro 配置
│
├── web/                      # Web 专用 (可选)
│   ├── src/
│   │   ├── components/ui/   # shadcn/ui 组件
│   │   └── ...
│   └── index.html
│
└── docs/                     # 文档
    └── SPEC.md
```

### 数据模型

```typescript
interface NewsItem {
  id: string;
  title_zh: string;
  title_en?: string;
  summary_zh: string;
  summary_en?: string;
  content_zh: string;
  content_en?: string;
  source_zh: string;
  source_en?: string;
  source_url: string;
  lang: 'zh' | 'en' | 'both';
  category: string;
  published_at: string;
  created_at: string;
  quality: {
    total_100: number;
    grade: 'A+' | 'A' | 'B' | 'C' | 'D';
    scores: QualityScores;
  };
  is_read?: boolean;
  is_favorited?: boolean;
  audio_url?: string;
}

interface QualityScores {
  completeness: number;      // 完整性
  language: number;          // 语言质量
  title: number;             // 标题质量
  source_credibility: number; // 来源可信度
  info_density: number;      // 信息密度
  actionability: number;     // 可操作性
  impact: number;            // 影响范围
  originality: number;       // 原创性
}
```

### API 设计

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/news` | GET | 获取资讯列表 |
| `/api/news/{id}` | GET | 获取资讯详情 |
| `/api/news/date/{date}` | GET | 获取指定日期资讯 |
| `/api/news/category/{cat}` | GET | 获取分类资讯 |
| `/api/news/{id}/audio` | POST | 生成 TTS 音频 |
| `/api/news/{id}/favorite` | POST | 收藏/取消收藏 |

### 质量评分标准

| 等级 | 分数 | 展示策略 |
|------|------|----------|
| A+ | 85-100 | 优先展示，质量标签 |
| A | 75-84 | 正常展示 |
| B | 65-74 | 正常展示 |
| C | 55-64 | 可选展示 |
| D | <55 | **不展示** |

---

## 📅 开发计划

### Phase 1: 前端重构
- [ ] 更新 UI 组件库，参考 shadcn/ui
- [ ] 重构日期选择器（滚轮式动画）
- [ ] 重构分类标签栏（滑动切换动画）
- [ ] 优化资讯卡片样式
- [ ] 实现下拉刷新

### Phase 2: 功能完善
- [ ] 日期筛选功能
- [ ] 质量过滤（不展示 D 级）
- [ ] TTS 朗读集成
- [ ] 收藏功能

### Phase 3: LLM 分类
- [ ] 调用 LLM 分析资讯类别
- [ ] 缓存分类结果
- [ ] 分类标签动态化

### Phase 4: 多端适配
- [ ] 微信小程序适配
- [ ] Web 端优化
- [ ] 响应式布局

---

## 🐛 已知问题

- [ ] 前端数据加载问题需排查
- [ ] 分类动画需优化
- [ ] 日期选择器待实现

---

## 📝 更新日志

### v0.3.0 (2026-04-28)
- 重命名项目为 TechEcho Pro
- 创建新分支 feature/techecho-redesign
- 开始参考 shadcn/ui 重构 UI
