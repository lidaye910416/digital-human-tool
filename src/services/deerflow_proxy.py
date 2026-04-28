"""
DeerFlow API 代理服务
将本地请求转发到 DeerFlow Docker 容器

用法:
    python deerflow_proxy.py  # 启动代理在 8888 端口
"""

import http.server
import socketserver
import subprocess
import json
import sys
import threading
import time

# DeerFlow 容器信息
DEERFLOW_GATEWAY = "deer-flow-gateway"
DEERFLOW_LANGGRAPH = "deer-flow-langgraph"
INTERNAL_PORT = "8001"  # Gateway API
LANGGRAPH_PORT = "2024"  # LangGraph API

# 本地代理端口
PROXY_PORT = 8888


class DeerFlowProxy(http.server.BaseHTTPRequestHandler):
    """DeerFlow API 代理处理器"""
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[DeerFlow Proxy] {args[0]}")
    
    def do_proxy(self, method="GET"):
        """代理请求到 DeerFlow Gateway"""
        path = self.path
        
        # 构建 curl 命令
        cmd = [
            "docker", "exec", "-i", DEERFLOW_GATEWAY,
            "curl", "-s", "-X", method,
            f"http://localhost:{INTERNAL_PORT}{path}"
        ]
        
        # 处理请求体
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            # 将请求体写入临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
                f.write(body)
                f.flush()
                temp_path = f.name
            
            cmd.extend(["-H", f"Content-Length: {content_length}"])
            cmd[4:4] = ["curl", "-s", "-X", method, "-d", f"@/dev/stdin"]
            # 简化：使用 --data-binary
            cmd = [
                "docker", "exec", "-i", DEERFLOW_GATEWAY,
                "sh", "-c",
                f"curl -s -X {method} -H 'Content-Type: application/json' -d '{body.decode()}' http://localhost:{INTERNAL_PORT}{path}'"
            ]
        
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60
            )
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(result.stdout.encode() if isinstance(result.stdout, str) else result.stdout)
            
        except subprocess.TimeoutExpired:
            self.send_error(504, "Gateway Timeout")
        except Exception as e:
            self.send_error(500, str(e))
    
    def do_GET(self):
        self.do_proxy("GET")
    
    def do_POST(self):
        self.do_proxy("POST")
    
    def do_PUT(self):
        self.do_proxy("PUT")
    
    def do_DELETE(self):
        self.do_proxy("DELETE")


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """多线程 HTTP 服务器"""
    allow_reuse_address = True


def check_deerflow_status():
    """检查 DeerFlow 状态"""
    print("\n🔍 检查 DeerFlow 状态...")
    
    try:
        # 检查容器状态
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=deer-flow", "--format", "{{.Names}}\t{{.Status}}"],
            capture_output=True, text=True
        )
        
        print("\n📦 DeerFlow 容器:")
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('\t')
                name = parts[0].replace('deer-flow-', '')
                status = parts[1] if len(parts) > 1 else 'unknown'
                is_running = 'running' in status.lower() and 'up' in status.lower()
                icon = "✅" if is_running else "❌"
                print(f"   {icon} {name}: {status}")
        
        # 测试 Gateway API
        print("\n🌐 Gateway API:")
        result = subprocess.run(
            ["docker", "exec", "deer-flow-gateway", "curl", "-s", "localhost:8001/health"],
            capture_output=True, text=True, timeout=10
        )
        if result.stdout:
            print(f"   ✅ {result.stdout.strip()}")
        else:
            print(f"   ❌ 无法连接")
            
    except Exception as e:
        print(f"   ❌ 检查失败: {e}")


def start_proxy():
    """启动代理服务"""
    server = ThreadedHTTPServer(("localhost", PROXY_PORT), DeerFlowProxy)
    print(f"🚀 DeerFlow 代理已启动: http://localhost:{PROXY_PORT}")
    print(f"   Gateway API: http://localhost:{PROXY_PORT}/api/*")
    print(f"   Health: http://localhost:{PROXY_PORT}/health")
    print("\n按 Ctrl+C 停止服务\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 代理服务已停止")
        server.shutdown()


def test_proxy():
    """测试代理"""
    print("\n🧪 测试 DeerFlow API...")
    
    import urllib.request
    
    base_url = f"http://localhost:{PROXY_PORT}"
    
    tests = [
        ("/health", "健康检查"),
        ("/api/models", "获取模型列表"),
        ("/api/skills", "获取技能列表"),
    ]
    
    for path, name in tests:
        print(f"\n   {name} ({path}):")
        try:
            with urllib.request.urlopen(f"{base_url}{path}", timeout=10) as resp:
                data = json.loads(resp.read())
                if "models" in data:
                    print(f"      ✅ 找到 {len(data['models'])} 个模型")
                elif "skills" in data:
                    print(f"      ✅ 找到 {len(data['skills'])} 个技能")
                else:
                    print(f"      ✅ {str(data)[:100]}")
        except Exception as e:
            print(f"      ❌ {e}")


if __name__ == "__main__":
    # 检查 DeerFlow 状态
    check_deerflow_status()
    
    # 如果指定了 --test 参数，只测试不启动
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_proxy()
    else:
        start_proxy()
