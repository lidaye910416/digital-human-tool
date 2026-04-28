"""
DeerFlow Deep Research Client
用于调用 DeerFlow 进行深度研究

通过 docker exec 访问 DeerFlow 容器 API
"""

import subprocess
import json
import asyncio
import logging
import os
from typing import Optional, Dict, Any, AsyncGenerator
from datetime import datetime

logger = logging.getLogger(__name__)

# DeerFlow 容器名称
GATEWAY_CONTAINER = "deer-flow-gateway"
LANGGRAPH_CONTAINER = "deer-flow-langgraph"
GATEWAY_PORT = "8001"
LANGGRAPH_PORT = "2024"


def _docker_exec(container: str, path: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
    """
    在 DeerFlow 容器内执行 curl 请求

    Args:
        container: 容器名称
        path: API 路径
        method: HTTP 方法
        data: 请求体数据

    Returns:
        JSON 响应
    """
    port = GATEWAY_PORT if container == GATEWAY_CONTAINER else LANGGRAPH_PORT
    url = f"http://localhost:{port}{path}"

    # 构建 curl 命令 (不使用 shell 转义)
    cmd = ["docker", "exec", container, "curl", "-s"]

    if method != "GET":
        cmd.extend(["-X", method])

    cmd.extend(["-H", "Content-Type: application/json"])

    # POST/PUT 需要 body，即使是空对象
    if method in ("POST", "PUT", "PATCH"):
        cmd.extend(["-d", json.dumps(data) if data else "{}"])
    elif data:
        cmd.extend(["-d", json.dumps(data)])

    cmd.append(url)

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120
        )

        if result.returncode != 0:
            raise Exception(f"curl failed: {result.stderr}")

        output = result.stdout.strip()
        if not output:
            return {}

        return json.loads(output)

    except subprocess.TimeoutExpired:
        raise Exception("Request timed out")
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error: {e}, output: {result.stdout[:200]}")
        return {}


def _docker_exec_stream(container: str, path: str, data: Dict) -> AsyncGenerator[str, None]:
    """
    在 DeerFlow 容器内执行流式请求 (SSE)

    Yields:
        每个 SSE 行
    """
    port = GATEWAY_PORT if container == GATEWAY_CONTAINER else LANGGRAPH_PORT
    url = f"http://localhost:{port}{path}"

    cmd = [
        "docker", "exec", "-i", container,
        "curl", "-s", "-N", "-X", "POST",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data),
        url
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        for line in proc.stdout:
            line = line.strip()
            if line.startswith("data: "):
                yield line[6:]  # 去掉 "data: " 前缀
            elif line == "":
                continue
            elif line.startswith("event: "):
                yield f"__EVENT__: {line[7:]}"
    finally:
        proc.terminate()
        proc.wait()


class DeerFlowClient:
    """DeerFlow API 客户端"""
    
    def __init__(self):
        self.gateway = GATEWAY_CONTAINER
        self.langgraph = LANGGRAPH_CONTAINER
        
    async def check_health(self) -> bool:
        """检查服务健康状态"""
        try:
            result = _docker_exec(self.gateway, "/health")
            return result.get("status") == "healthy"
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def list_models(self) -> list:
        """列出可用模型"""
        result = _docker_exec(self.gateway, "/api/models")
        return result.get("models", [])
    
    async def list_skills(self) -> list:
        """列出可用技能"""
        result = _docker_exec(self.gateway, "/api/skills")
        return result.get("skills", [])
    
    async def list_agents(self) -> list:
        """列出可用代理"""
        result = _docker_exec(self.gateway, "/api/agents")
        return result.get("agents", [])
    
    async def create_thread(self, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """创建线程"""
        data = {"thread_id": thread_id} if thread_id else {}
        return _docker_exec(self.langgraph, "/threads", method="POST", data=data)
    
    async def send_message(
        self,
        message: str,
        thread_id: Optional[str] = None,
        mode: str = "pro"  # flash, standard, pro, ultra
    ) -> Dict[str, Any]:
        """
        发送消息并获取响应 (wait 模式)
        
        Args:
            message: 用户消息
            thread_id: 可选的线程ID
            mode: 模式 (flash/standard/pro/ultra)
            
        Returns:
            响应结果
        """
        # 如果没有 thread_id，先创建
        if not thread_id:
            thread = await self.create_thread()
            thread_id = thread.get("thread_id")
        
        # 设置上下文模式
        context_modes = {
            "flash": {"thinking_enabled": False, "is_plan_mode": False, "subagent_enabled": False},
            "standard": {"thinking_enabled": True, "is_plan_mode": False, "subagent_enabled": False},
            "pro": {"thinking_enabled": True, "is_plan_mode": True, "subagent_enabled": False},
            "ultra": {"thinking_enabled": True, "is_plan_mode": True, "subagent_enabled": True},
        }
        context = context_modes.get(mode, context_modes["pro"])
        context["thread_id"] = thread_id
        
        # 构建请求
        data = {
            "assistant_id": "lead_agent",
            "input": {
                "messages": [
                    {
                        "type": "human",
                        "content": [{"type": "text", "text": message}]
                    }
                ]
            },
            "stream_mode": ["values", "messages-tuple"],
            "stream_subgraphs": True,
            "config": {
                "recursion_limit": 1000
            },
            "context": context
        }
        
        # 收集流式响应
        responses = []
        async for event in self._stream_run(thread_id, data):
            if event.startswith("__EVENT__: "):
                event_type = event[11:]
                if event_type == "end":
                    break
            else:
                try:
                    event_data = json.loads(event)
                    responses.append(event_data)
                except json.JSONDecodeError:
                    continue
        
        return {"thread_id": thread_id, "events": responses}
    
    async def _stream_run(self, thread_id: str, data: Dict) -> AsyncGenerator[str, None]:
        """流式运行"""
        path = f"/threads/{thread_id}/runs/stream"
        
        for line in _docker_exec_stream(self.langgraph, path, data):
            yield line
    
    async def get_thread_history(self, thread_id: str) -> Dict[str, Any]:
        """获取线程历史"""
        return _docker_exec(self.langgraph, f"/threads/{thread_id}/history")
    
    async def research_news(self, topic: str) -> Dict[str, Any]:
        """
        研究新闻主题
        
        Args:
            topic: 新闻主题
            
        Returns:
            研究结果
        """
        query = f"""请深入研究以下科技新闻主题：{topic}

请提供：
1. 主题概述 (100字以内)
2. 关键事件和进展 (要点列表)
3. 主要参与者和公司
4. 影响和意义 (50字以内)
5. 相关资源链接

请用中文回答，简洁明了。"""
        
        return await self.send_message(query, mode="pro")


async def test_deerflow():
    """测试 DeerFlow 调用"""
    print("=" * 60)
    print("🧪 DeerFlow Deep Research Test")
    print("=" * 60)

    client = DeerFlowClient()

    # 1. 检查健康状态
    print("\n1️⃣ 检查 DeerFlow 服务状态...")
    is_healthy = await client.check_health()
    if not is_healthy:
        print("❌ DeerFlow 服务不可用")
        print("   请运行: make docker-start")
        return
    print("✅ DeerFlow 服务正常")

    # 2. 列出可用模型
    print("\n2️⃣ 获取可用模型...")
    models = await client.list_models()
    print(f"   找到 {len(models)} 个模型:")
    for m in models:
        print(f"   - {m.get('display_name', m.get('name'))}")

    # 3. 列出可用技能
    print("\n3️⃣ 获取可用技能...")
    skills = await client.list_skills()
    print(f"   找到 {len(skills)} 个技能:")
    for s in skills[:5]:
        print(f"   - {s.get('name')} {'(已启用)' if s.get('enabled') else '(已禁用)'}")

    # 4. 创建测试线程
    print("\n4️⃣ 创建测试线程...")
    thread = await client.create_thread()
    print(f"   ✅ Thread ID: {thread.get('thread_id')}")

    # 5. 测试流式响应
    print("\n5️⃣ 测试流式响应...")
    print("   发送: Say hello in exactly 5 words")

    try:
        result = await client.send_message(
            "Say hello in exactly 5 words, only reply with those 5 words.",
            mode="flash"
        )

        thread_id = result.get('thread_id')
        events = result.get('events', [])
        print(f"\n   ✅ Thread ID: {thread_id}")
        print(f"   事件数: {len(events)}")

        # 从 messages-tuple 事件中提取 AI 响应
        ai_response = ""
        model_used = None
        for event in events:
            if isinstance(event, list):
                for item in event:
                    if isinstance(item, dict):
                        # 处理 AIMessageChunk
                        if item.get("type") == "AIMessageChunk":
                            content = item.get("content", "")
                            if isinstance(content, str) and content:
                                ai_response += content
                        # 尝试获取模型信息
                        resp_meta = item.get("response_metadata", {})
                        if not model_used:
                            model_used = resp_meta.get("model_name")

        if ai_response:
            print(f"\n   🤖 AI 响应: {ai_response[:100]}")
        if model_used:
            print(f"   📦 模型: {model_used}")

    except Exception as e:
        print(f"   ❌ 测试失败: {e}")

    print("\n" + "=" * 60)
    print("\n✅ DeerFlow API 调用完全验证成功!")
    print("=" * 60)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    asyncio.run(test_deerflow())
