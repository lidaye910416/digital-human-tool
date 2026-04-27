# CLAUDE.md

数字人播报视频生成器 - 项目开发指南

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

## 📖 开发准则

1. **遵循 Karpathy 准则** - 每次修改前先思考，确保最小化变更
2. **验证后再提交** - 使用测试 Agent 验证功能
3. **记录变更** - 保持本文档更新
4. **代码质量优先** - 简洁、可维护、可测试
