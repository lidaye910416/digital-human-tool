# 数字人播报视频生成器

## 快速开始

1. 安装依赖：
```bash
pip install -e .
```

2. 复制环境变量：
```bash
cp .env.example .env
# 编辑 .env 填入你的 MiniMax API Key
```

3. 启动服务：
```bash
./scripts/run.sh
```

4. 访问 http://localhost:8000/docs 查看 API 文档

## 项目结构

```
src/
├── main.py              # FastAPI 入口
├── config.py            # 配置
├── api/                 # API 路由
├── models/              # 数据库模型
├── services/            # 业务服务
└── utils/               # 工具函数

tests/                   # 测试文件
```

## API 端点

- POST /api/users/register - 用户注册
- POST /api/users/login - 用户登录
- POST /api/avatars/generate-ai - AI 生成数字人
- GET /api/avatars - 获取数字人列表
- GET /api/scenes - 获取场景列表
- POST /api/projects - 创建项目
- POST /api/projects/{id}/generate - 生成视频
- GET /api/projects - 获取项目列表
