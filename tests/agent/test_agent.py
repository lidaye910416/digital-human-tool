"""
数字人视频生成系统 - 测试 Agent
基于 MiniMax API 的专业测试框架
"""

import httpx
import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

class TestStatus(Enum):
    PASS = "✅ PASS"
    FAIL = "❌ FAIL"
    SKIP = "⏭️ SKIP"
    WARN = "⚠️ WARN"

class TestCategory(Enum):
    SYSTEM = "系统测试"
    API = "API测试"
    TTS = "TTS语音测试"
    VIDEO = "视频生成测试"
    AVATAR = "数字人测试"
    INTEGRATION = "集成测试"

@dataclass
class TestResult:
    name: str
    category: TestCategory
    status: TestStatus
    message: str
    duration: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TestReport:
    timestamp: str
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    warnings: int = 0
    results: List[TestResult] = field(default_factory=list)
    
    def add_result(self, result: TestResult):
        self.results.append(result)
        self.total_tests += 1
        if result.status == TestStatus.PASS:
            self.passed += 1
        elif result.status == TestStatus.FAIL:
            self.failed += 1
        elif result.status == TestStatus.SKIP:
            self.skipped += 1
        elif result.status == TestStatus.WARN:
            self.warnings += 1
    
    def get_summary(self) -> str:
        success_rate = (self.passed / self.total_tests * 100) if self.total_tests > 0 else 0
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                   测试报告摘要                               ║
╠══════════════════════════════════════════════════════════════╣
║  测试时间: {self.timestamp}
║  总测试数: {self.total_tests}
║  通过:     {self.passed} ({success_rate:.1f}%)
║  失败:     {self.failed}
║  跳过:     {self.skipped}
║  警告:     {self.warnings}
╚══════════════════════════════════════════════════════════════╝
"""
    
    def to_json(self) -> str:
        return json.dumps({
            "timestamp": self.timestamp,
            "total": self.total_tests,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "warnings": self.warnings,
            "success_rate": f"{(self.passed/self.total_tests*100):.1f}%" if self.total_tests > 0 else "0%",
            "results": [
                {
                    "name": r.name,
                    "category": r.category.value,
                    "status": r.status.value,
                    "message": r.message,
                    "duration": f"{r.duration:.3f}s",
                    "details": r.details
                }
                for r in self.results
            ]
        }, ensure_ascii=False, indent=2)


class DigitalHumanTestAgent:
    """数字人视频生成系统测试 Agent"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
        self.report = TestReport(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.test_data = {
            "user_id": 1,
            "avatar_id": None,
            "project_id": None,
            "voice_id": "female-tianmei"
        }
    
    async def close(self):
        await self.client.aclose()
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送 API 请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = await self.client.request(method, url, **kwargs)
            return {
                "status_code": response.status_code,
                "data": response.json() if response.text else {},
                "error": None
            }
        except Exception as e:
            return {
                "status_code": 0,
                "data": {},
                "error": str(e)
            }
    
    async def _run_test(
        self,
        name: str,
        category: TestCategory,
        test_func,
        *args,
        **kwargs
    ) -> TestResult:
        """运行单个测试"""
        start_time = time.time()
        try:
            result = await test_func(*args, **kwargs)
            duration = time.time() - start_time
            return TestResult(
                name=name,
                category=category,
                status=result["status"],
                message=result["message"],
                duration=duration,
                details=result.get("details", {})
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name=name,
                category=category,
                status=TestStatus.FAIL,
                message=f"测试异常: {str(e)}",
                duration=duration
            )
    
    # ========== 系统测试 ==========
    
    async def test_health_check(self):
        """测试健康检查"""
        response = await self._request("GET", "/health")
        if response["error"]:
            return {"status": TestStatus.FAIL, "message": f"连接失败: {response['error']}"}
        
        if response["status_code"] == 200 and response["data"].get("status") == "healthy":
            return {"status": TestStatus.PASS, "message": "服务运行正常"}
        return {"status": TestStatus.FAIL, "message": f"健康检查失败: {response['data']}"}
    
    async def test_api_status(self):
        """测试 API 状态"""
        response = await self._request("GET", "/api/status")
        if response["error"]:
            return {"status": TestStatus.FAIL, "message": f"连接失败: {response['error']}"}
        
        data = response["data"]
        minimax_ok = data.get("minimax_api_key_set", False)
        tts_ok = data.get("minimax_api", {}).get("tts", {}).get("available", False)
        video_ok = data.get("minimax_api", {}).get("video", {}).get("available", False)
        
        details = {
            "minimax_api_key": minimax_ok,
            "tts_available": tts_ok,
            "video_available": video_ok
        }
        
        if minimax_ok and tts_ok:
            return {
                "status": TestStatus.PASS,
                "message": f"TTS: {'✅' if tts_ok else '❌'} | 视频: {'✅' if video_ok else '❌'}",
                "details": details
            }
        return {"status": TestStatus.FAIL, "message": "API 未正确配置", "details": details}
    
    # ========== 语音测试 ==========
    
    async def test_get_voices(self):
        """测试获取声音列表"""
        response = await self._request("GET", "/api/voices")
        if response["error"]:
            return {"status": TestStatus.FAIL, "message": f"连接失败: {response['error']}"}
        
        voices = response["data"].get("voices", [])
        female_count = len([v for v in voices if v.get("gender") == "female"])
        male_count = len([v for v in voices if v.get("gender") == "male"])
        
        details = {
            "total_voices": len(voices),
            "female_voices": female_count,
            "male_voices": male_count,
            "voices": [v["id"] for v in voices]
        }
        
        if len(voices) >= 9:
            return {
                "status": TestStatus.PASS,
                "message": f"共 {len(voices)} 种声音 (女: {female_count}, 男: {male_count})",
                "details": details
            }
        return {"status": TestStatus.WARN, "message": f"声音数量较少: {len(voices)}", "details": details}
    
    async def test_voice_presets(self):
        """测试声音预设"""
        response = await self._request("GET", "/api/voices/presets")
        if response["error"]:
            return {"status": TestStatus.FAIL, "message": f"连接失败: {response['error']}"}
        
        presets = response["data"].get("presets", [])
        if presets:
            return {
                "status": TestStatus.PASS,
                "message": f"获取到 {len(presets)} 个预设",
                "details": {"presets": [p["name"] for p in presets]}
            }
        return {"status": TestStatus.FAIL, "message": "无预设可用"}
    
    async def test_tts_synthesis(self):
        """测试 TTS 语音合成"""
        response = await self._request(
            "POST",
            "/api/voices/test",
            json={
                "text": "这是一段测试语音，用于验证 TTS 功能是否正常工作。",
                "voice_id": self.test_data["voice_id"],
                "speed": 1.0
            }
        )
        if response["error"]:
            return {"status": TestStatus.FAIL, "message": f"连接失败: {response['error']}"}
        
        if response["status_code"] == 200 and response["data"].get("success"):
            audio_url = response["data"].get("audio_url", "")
            has_url = audio_url and not audio_url.startswith("data:")
            return {
                "status": TestStatus.PASS if has_url else TestStatus.WARN,
                "message": f"TTS 生成{'成功 (URL可用)' if has_url else '成功 (Base64)'}",
                "details": {"audio_url": audio_url[:50] + "..." if len(audio_url) > 50 else audio_url}
            }
        return {"status": TestStatus.FAIL, "message": f"TTS 失败: {response['data']}"}
    
    # ========== 数字人测试 ==========
    
    async def test_create_avatar(self):
        """测试创建 AI 数字人"""
        response = await self._request(
            "POST",
            "/api/avatars/generate-ai",
            json={
                "user_id": self.test_data["user_id"],
                "gender": "female",
                "age": "young",
                "style": "professional"
            }
        )
        if response["error"]:
            return {"status": TestStatus.FAIL, "message": f"连接失败: {response['error']}"}
        
        if response["status_code"] == 200:
            avatar_id = response["data"].get("id")
            self.test_data["avatar_id"] = avatar_id
            return {
                "status": TestStatus.PASS,
                "message": f"创建数字人成功 (ID: {avatar_id})",
                "details": {"avatar_id": avatar_id, "image_url": response["data"].get("image_url")}
            }
        return {"status": TestStatus.FAIL, "message": f"创建失败: {response['data']}"}
    
    async def test_photo_avatar(self):
        """测试照片数字人"""
        response = await self._request(
            "POST",
            "/api/avatars/from-photo",
            json={
                "user_id": self.test_data["user_id"],
                "photo_url": "https://example.com/test-photo.jpg",
                "name": "测试照片形象"
            }
        )
        if response["error"]:
            return {"status": TestStatus.FAIL, "message": f"连接失败: {response['error']}"}
        
        if response["status_code"] == 200:
            return {
                "status": TestStatus.PASS,
                "message": "照片数字人创建成功",
                "details": {"avatar_id": response["data"].get("id")}
            }
        return {"status": TestStatus.FAIL, "message": f"创建失败: {response['data']}"}
    
    async def test_get_avatars(self):
        """测试获取数字人列表"""
        response = await self._request("GET", f"/api/avatars?user_id={self.test_data['user_id']}")
        if response["error"]:
            return {"status": TestStatus.FAIL, "message": f"连接失败: {response['error']}"}
        
        avatars = response["data"] if isinstance(response["data"], list) else []
        return {
            "status": TestStatus.PASS,
            "message": f"获取到 {len(avatars)} 个数字人",
            "details": {"count": len(avatars)}
        }
    
    # ========== 场景测试 ==========
    
    async def test_get_scenes(self):
        """测试获取场景列表"""
        response = await self._request("GET", "/api/scenes")
        if response["error"]:
            return {"status": TestStatus.FAIL, "message": f"连接失败: {response['error']}"}
        
        scenes = response["data"] if isinstance(response["data"], list) else []
        return {
            "status": TestStatus.PASS if scenes else TestStatus.WARN,
            "message": f"获取到 {len(scenes)} 个场景",
            "details": {"scenes": [s.get("name") for s in scenes]}
        }
    
    async def test_scene_presets(self):
        """测试获取场景预设"""
        response = await self._request("GET", "/api/scenes/presets")
        if response["error"]:
            return {"status": TestStatus.FAIL, "message": f"连接失败: {response['error']}"}
        
        presets = response["data"]
        if isinstance(presets, dict):
            categories = list(presets.keys())
            return {
                "status": TestStatus.PASS,
                "message": f"获取到 {len(categories)} 个场景分类",
                "details": {"categories": categories}
            }
        return {"status": TestStatus.FAIL, "message": "场景预设格式错误"}
    
    # ========== 项目测试 ==========
    
    async def test_create_project(self):
        """测试创建视频项目"""
        if not self.test_data["avatar_id"]:
            return {"status": TestStatus.SKIP, "message": "跳过 (无 avatar_id)"}
        
        response = await self._request(
            "POST",
            "/api/projects",
            json={
                "user_id": self.test_data["user_id"],
                "title": "Agent 测试项目",
                "script_text": "这是由测试 Agent 自动创建的样例项目，用于验证视频生成功能是否正常。",
                "avatar_id": self.test_data["avatar_id"],
                "voice_config": {"voice_id": self.test_data["voice_id"], "speed": 1.0}
            }
        )
        if response["error"]:
            return {"status": TestStatus.FAIL, "message": f"连接失败: {response['error']}"}
        
        if response["status_code"] == 200:
            project_id = response["data"].get("id")
            self.test_data["project_id"] = project_id
            return {
                "status": TestStatus.PASS,
                "message": f"创建项目成功 (ID: {project_id})",
                "details": {"project_id": project_id}
            }
        return {"status": TestStatus.FAIL, "message": f"创建失败: {response['data']}"}
    
    async def test_get_projects(self):
        """测试获取项目列表"""
        response = await self._request("GET", f"/api/projects?user_id={self.test_data['user_id']}")
        if response["error"]:
            return {"status": TestStatus.FAIL, "message": f"连接失败: {response['error']}"}
        
        projects = response["data"] if isinstance(response["data"], list) else []
        return {
            "status": TestStatus.PASS,
            "message": f"获取到 {len(projects)} 个项目",
            "details": {"count": len(projects)}
        }
    
    async def test_get_project_detail(self):
        """测试获取项目详情"""
        if not self.test_data["project_id"]:
            return {"status": TestStatus.SKIP, "message": "跳过 (无 project_id)"}
        
        response = await self._request("GET", f"/api/projects/{self.test_data['project_id']}")
        if response["error"]:
            return {"status": TestStatus.FAIL, "message": f"连接失败: {response['error']}"}
        
        if response["status_code"] == 200:
            return {
                "status": TestStatus.PASS,
                "message": "项目详情获取成功",
                "details": {"title": response["data"].get("title")}
            }
        return {"status": TestStatus.FAIL, "message": f"获取失败: {response['data']}"}
    
    # ========== 视频生成测试 ==========
    
    async def test_video_generation(self):
        """测试视频生成 (核心功能)"""
        if not self.test_data["project_id"]:
            return {"status": TestStatus.SKIP, "message": "跳过 (无 project_id)"}
        
        print(f"\n⏳ 正在生成视频 (项目 ID: {self.test_data['project_id']})...")
        response = await self._request(
            "POST",
            f"/api/projects/{self.test_data['project_id']}/generate"
        )
        
        if response["error"]:
            return {"status": TestStatus.FAIL, "message": f"连接失败: {response['error']}"}
        
        data = response["data"]
        video_url = data.get("video_url", "")
        audio_url = data.get("audio_url", "")
        status = data.get("status")
        
        details = {
            "status": status,
            "has_video_url": bool(video_url and not video_url.startswith("data:")),
            "has_audio_url": bool(audio_url),
            "video_url": video_url[:60] + "..." if video_url else None,
            "credits_used": data.get("credits_used")
        }
        
        if status == "completed":
            if video_url and not video_url.startswith("data:"):
                return {
                    "status": TestStatus.PASS,
                    "message": f"视频生成成功! task_id: {video_url.split('/')[-1]}",
                    "details": details
                }
            else:
                return {
                    "status": TestStatus.WARN,
                    "message": "TTS 成功，视频生成需要额外配置",
                    "details": details
                }
        return {"status": TestStatus.FAIL, "message": f"视频生成失败: {data}"}
    
    # ========== 导出测试 ==========
    
    async def test_export_mp4(self):
        """测试导出 MP4"""
        if not self.test_data["project_id"]:
            return {"status": TestStatus.SKIP, "message": "跳过 (无 project_id)"}
        
        response = await self._request("GET", f"/api/export/{self.test_data['project_id']}/mp4")
        if response["error"]:
            return {"status": TestStatus.FAIL, "message": f"连接失败: {response['error']}"}
        
        if response["status_code"] == 200:
            return {
                "status": TestStatus.PASS,
                "message": "MP4 导出配置获取成功",
                "details": response["data"]
            }
        return {"status": TestStatus.FAIL, "message": f"导出失败: {response['data']}"}
    
    async def test_export_gif(self):
        """测试导出 GIF"""
        if not self.test_data["project_id"]:
            return {"status": TestStatus.SKIP, "message": "跳过 (无 project_id)"}
        
        response = await self._request("GET", f"/api/export/{self.test_data['project_id']}/gif")
        if response["error"]:
            return {"status": TestStatus.FAIL, "message": f"连接失败: {response['error']}"}
        
        if response["status_code"] == 200:
            return {
                "status": TestStatus.PASS,
                "message": "GIF 导出配置获取成功",
                "details": response["data"]
            }
        return {"status": TestStatus.FAIL, "message": f"导出失败: {response['data']}"}
    
    # ========== 语言测试 ==========
    
    async def test_get_languages(self):
        """测试获取支持的语言"""
        response = await self._request("GET", "/api/languages")
        if response["error"]:
            return {"status": TestStatus.FAIL, "message": f"连接失败: {response['error']}"}
        
        langs = response["data"].get("languages", [])
        return {
            "status": TestStatus.PASS,
            "message": f"支持 {len(langs)} 种语言",
            "details": {"languages": [l["code"] for l in langs]}
        }
    
    # ========== 运行所有测试 ==========
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║          数字人视频生成系统 - 自动化测试 Agent                 ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        tests = [
            # 系统测试
            ("健康检查", TestCategory.SYSTEM, self.test_health_check),
            ("API 状态检查", TestCategory.SYSTEM, self.test_api_status),
            
            # 语音测试
            ("获取声音列表", TestCategory.TTS, self.test_get_voices),
            ("获取声音预设", TestCategory.TTS, self.test_voice_presets),
            ("TTS 语音合成", TestCategory.TTS, self.test_tts_synthesis),
            
            # 数字人测试
            ("创建 AI 数字人", TestCategory.AVATAR, self.test_create_avatar),
            ("创建照片数字人", TestCategory.AVATAR, self.test_photo_avatar),
            ("获取数字人列表", TestCategory.AVATAR, self.test_get_avatars),
            
            # 场景测试
            ("获取场景列表", TestCategory.API, self.test_get_scenes),
            ("获取场景预设", TestCategory.API, self.test_scene_presets),
            
            # 项目测试
            ("创建视频项目", TestCategory.VIDEO, self.test_create_project),
            ("获取项目列表", TestCategory.VIDEO, self.test_get_projects),
            ("获取项目详情", TestCategory.VIDEO, self.test_get_project_detail),
            
            # 视频生成测试
            ("视频生成 (核心)", TestCategory.VIDEO, self.test_video_generation),
            
            # 导出测试
            ("导出 MP4", TestCategory.VIDEO, self.test_export_mp4),
            ("导出 GIF", TestCategory.VIDEO, self.test_export_gif),
            
            # 语言测试
            ("获取支持语言", TestCategory.API, self.test_get_languages),
        ]
        
        for name, category, test_func in tests:
            print(f"\n🔍 测试: {name}...", end=" ", flush=True)
            result = await self._run_test(name, category, test_func)
            self.report.add_result(result)
            print(result.status.value)
            if result.status == TestStatus.FAIL:
                print(f"   └─ {result.message}")
            elif result.details:
                print(f"   └─ {result.details}")
        
        # 输出报告
        print(self.report.get_summary())
        
        # 按类别统计
        print("\n📊 按类别统计:")
        categories = {}
        for result in self.report.results:
            cat = result.category.value
            if cat not in categories:
                categories[cat] = {"total": 0, "passed": 0, "failed": 0}
            categories[cat]["total"] += 1
            if result.status == TestStatus.PASS:
                categories[cat]["passed"] += 1
            elif result.status == TestStatus.FAIL:
                categories[cat]["failed"] += 1
        
        for cat, stats in categories.items():
            rate = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"   {cat}: {stats['passed']}/{stats['total']} ({rate:.0f}%)")
        
        # 保存报告
        report_file = f"/Users/jasonlee/digital-human-tool/tests/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(self.report.to_json())
        print(f"\n📄 详细报告已保存: {report_file}")
        
        return self.report


async def main():
    """主函数"""
    agent = DigitalHumanTestAgent()
    try:
        report = await agent.run_all_tests()
        
        # 返回退出码
        if report.failed > 0:
            print("\n⚠️  部分测试失败，请检查上述报告")
            return 1
        else:
            print("\n✅ 所有测试通过!")
            return 0
    finally:
        await agent.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
