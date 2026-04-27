# 数字人视频生成系统 - 测试 Agent

## 概述

这是一个自动化测试 Agent，用于全面测试数字人视频生成系统的所有功能模块。

## 功能特点

- ✅ 17 个测试用例，覆盖所有核心功能
- ✅ 异步 HTTP 请求，测试效率高
- ✅ 详细的测试报告生成
- ✅ 按类别统计测试结果
- ✅ 支持跳过依赖测试

## 测试覆盖

| 类别 | 测试项 |
|------|--------|
| 系统测试 | 健康检查、API 状态检查 |
| TTS 语音测试 | 获取声音列表、获取声音预设、TTS 语音合成 |
| 数字人测试 | 创建 AI 数字人、创建照片数字人、获取数字人列表 |
| API 测试 | 获取场景列表、获取场景预设、获取支持语言 |
| 视频生成测试 | 创建视频项目、获取项目列表、获取项目详情、视频生成、导出 MP4、导出 GIF |

## 使用方法

### 运行所有测试

```bash
python3 tests/agent/test_agent.py
```

### 运行特定测试

```python
import asyncio
from test_agent import DigitalHumanTestAgent

async def main():
    agent = DigitalHumanTestAgent()
    
    # 运行单个测试
    result = await agent.test_health_check()
    print(result)
    
    await agent.close()

asyncio.run(main())
```

### 集成到 CI/CD

```python
import asyncio
import sys
from test_agent import DigitalHumanTestAgent

async def ci_test():
    agent = DigitalHumanTestAgent()
    try:
        report = await agent.run_all_tests()
        await agent.close()
        
        if report.failed > 0:
            # 保存报告并退出
            with open("test-report.json", "w") as f:
                f.write(report.to_json())
            return 1
        return 0
    finally:
        await agent.close()

exit_code = asyncio.run(ci_test())
exit(exit_code)
```

## 测试报告

运行后会生成 JSON 格式的测试报告，保存在 `tests/report_*.json`。

### 报告结构

```json
{
  "timestamp": "2026-04-26 11:11:37",
  "total": 17,
  "passed": 17,
  "failed": 0,
  "skipped": 0,
  "warnings": 0,
  "success_rate": "100.0%",
  "results": [
    {
      "name": "健康检查",
      "category": "系统测试",
      "status": "✅ PASS",
      "message": "服务运行正常",
      "duration": "0.031s",
      "details": {}
    }
  ]
}
```

## 扩展测试

要添加新的测试用例，在 `DigitalHumanTestAgent` 类中添加方法：

```python
async def test_new_feature(self):
    """测试新功能"""
    response = await self._request("GET", "/api/new-endpoint")
    
    if response["status_code"] == 200:
        return {
            "status": TestStatus.PASS,
            "message": "新功能正常",
            "details": response["data"]
        }
    return {"status": TestStatus.FAIL, "message": "新功能异常"}
```

然后在 `run_all_tests` 方法中注册：

```python
tests = [
    # ... 现有测试
    ("新功能测试", TestCategory.API, self.test_new_feature),
]
```

## 依赖

- Python 3.8+
- httpx
- (项目其他依赖)

安装依赖：
```bash
pip install httpx
```
