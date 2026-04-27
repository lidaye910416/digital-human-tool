# CLAUDE.md

> **当前分支**: `feature/image-to-video`  
> **当前版本**: v0.2.0 - Tech Echo 科技资讯播报平台

---

## 🎯 产品概述

**Tech Echo** - 科技资讯播报平台
- 收集科技资讯，按日期存储
- 支持阅读和 TTS 朗读
- 数字人播报（预留）

**目标用户**: 需要了解科技资讯的人群

**多端支持**: 微信小程序优先 (Taro)

---

## 🎯 分支目标

本分支专注于**图生视频 (Image-to-Video)** 功能的开发：
- 核心能力：输入一张图片 + 文本/音频 → 输出数字人说话视频
- 典型场景：静态照片 → 动态播报视频

---

# 数字人播报视频生成器 - 项目开发指南

> 本项目基于 [Andrej Karpathy](https://karpathy.github.io/) 编码准则编写，融合了 AI Coding Guidelines 和项目特定需求。

---

## 📋 Karpathy AI Coding Guidelines

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

---

## 🛠️ 项目特定说明

### 技术栈
- **后端**: Python FastAPI + SQLAlchemy + SQLite
- **前端**: React + TypeScript + Vite + Electron
- **桌面端**: Electron
- **AI 服务**: MiniMax API (文生图 + TTS + 视频生成)

### 项目结构
```
src/
├── api/           # API 路由
├── models/        # 数据库模型
├── services/     # 业务服务 (MiniMax 集成)
├── middleware/    # 中间件
└── utils/        # 工具函数

desktop/          # Electron 桌面客户端
  └── src-renderer/  # React 前端

tests/
├── agent/        # 测试 Agent
└── report_*.json # 测试报告
```

### 开发命令
```bash
# 后端服务
python3 -m uvicorn src.main:app --reload

# 前端开发
cd desktop && npm run dev

# 运行测试 Agent
python3 tests/agent/test_agent.py
```

### API 端点
| 端点 | 说明 |
|------|------|
| `/api/avatars/generate-ai` | AI 生成数字人 |
| `/api/avatars/from-photo` | 从照片创建数字人 |
| `/api/projects` | 创建视频项目 |
| `/api/projects/{id}/generate` | 生成视频 |
| `/api/voices/test` | TTS 语音测试 |
| `/api/scenes` | 获取场景列表 |

### 注意事项
- 所有 API 调用通过 MiniMax 云端服务，无需本地 GPU
- 使用本地文件系统存储用户数据和头像图片
- 积分制商业模式
- 头像图片存储在 `data/avatars/` 目录，通过 `/data` 路径访问

### MiniMax API 配置
```python
# TTS 语音合成
POST https://api.minimaxi.com/v1/t2a_v2
model: "speech-2.8-hd"
voice_id: "female-tianmei" 等

# 视频生成
POST https://api.minimaxi.com/v1/video_generation
model: "MiniMax-Hailuo-2.3" 或 "MiniMax-Hailuo-2.3-Fast"

# 图像生成
POST https://api.minimaxi.com/v1/image_generation
model: "image-01"
```

---

## 📋 图生视频功能规划

### 核心流程
```
图片 → 数字人形象 → TTS语音 → 唇形同步 → 最终视频
```

### 待实现功能
- [ ] 图片预处理（人脸检测、裁剪、对齐）
- [ ] 唇形同步（核心功能）
- [ ] 情感控制（高兴、严肃、平静）
- [ ] 背景保持（防止背景变形）
- [ ] 视频时长控制
- [ ] 多角色支持

### API 扩展
- `POST /api/video/generate` - 图生视频（核心功能）
- `POST /api/video/preview` - 预览生成效果
- `GET /api/video/{task_id}` - 查询生成状态

---

## 🔬 技术调研 - 唇形同步方案

### 方案对比

| 项目 | Stars | 难度 | GPU需求 | 推荐度 |
|------|-------|------|---------|--------|
| **SadTalker** | ⭐ 13.7k | 中 | 必须 | ⭐⭐⭐⭐⭐ |
| **Wav2Lip** | ⭐ 13k | 中 | 必须 | ⭐⭐⭐⭐ |
| **LatentSync** | ⭐ 5.6k | 低 | 推荐 | ⭐⭐⭐⭐ |
| **First-Order-Model** | ⭐ 5.2k | 低 | 可选 | ⭐⭐⭐ |
| **PaddleGAN** | ⭐ 8k | 低 | 推荐 | ⭐⭐⭐ |

### 方案详情

#### 1. SadTalker (CVPR 2023) ⭐ 推荐
- **仓库**: https://github.com/OpenTalker/SadTalker
- **优点**: 效果好，3D系数驱动，保持原图风格
- **缺点**: 需要GPU，部署复杂
- **适用**: 高质量需求

#### 2. Wav2Lip (ACM 2020)
- **仓库**: https://github.com/Rudrabha/Wav2Lip
- **优点**: 经典方案，稳定可靠
- **缺点**: 需要GPU，效果一般
- **适用**: 稳定优先

#### 3. LatentSync (字节跳动)
- **仓库**: https://github.com/bytedance/LatentSync
- **优点**: 基于Stable Diffusion，效果好
- **缺点**: 较新，文档少
- **适用**: 尝鲜用户

#### 4. First-Order-Model (轻量)
- **仓库**: https://github.com/AliaksandrSiarohin/first-order-model
- **优点**: 轻量，CPU可跑，部署简单
- **缺点**: 效果一般
- **适用**: 低配机器/快速原型

#### 5. PaddleGAN (百度飞桨)
- **仓库**: https://github.com/PaddlePaddle/PaddleGAN
- **优点**: 一个库集成多种能力
- **缺点**: 依赖飞桨生态
- **适用**: 百度用户

### TODO 清单

- [ ] **调研阶段** - 分析各方案优缺点
  - [x] SadTalker
  - [x] Wav2Lip
  - [x] LatentSync
  - [x] First-Order-Model
  - [x] PaddleGAN
- [ ] **选型决策** - 确定最终方案
- [ ] **集成开发** - 接入选定的唇形同步库
- [ ] **API封装** - 对外提供唇形同步接口
- [ ] **效果优化** - 根据实际效果调优

---

## 📖 开发准则

1. **遵循 Karpathy 准则** - 每次修改前先思考，确保最小化变更
2. **验证后再提交** - 使用测试 Agent 验证功能
3. **记录变更** - 保持本文档更新
4. **代码质量优先** - 简洁、可维护、可测试
