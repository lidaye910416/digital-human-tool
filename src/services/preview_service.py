"""
预览服务 - 基于模板图片生成场景预览
使用图片合成方式确保人物一致性
注意: MiniMax image-01 不支持真正的图生图，因此使用合成方式
"""
import logging
import httpx
import base64
from io import BytesIO
from typing import Optional, Tuple
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

logger = logging.getLogger(__name__)

# 场景配置 - 包含颜色和样式
SCENE_CONFIGS = {
    1: {"name": "现代办公室", "icon": "🏢", "colors": [(30, 35, 60), (20, 40, 80)], "prompt": "modern office"},
    2: {"name": "会议室", "icon": "🏛️", "colors": [(45, 55, 75), (55, 65, 85)], "prompt": "meeting room"},
    3: {"name": "专业演播室", "icon": "🎬", "colors": [(15, 15, 25), (25, 25, 40)], "prompt": "broadcast studio"},
    4: {"name": "新闻直播间", "icon": "📺", "colors": [(80, 60, 120), (100, 70, 140)], "prompt": "news studio"},
    5: {"name": "教室", "icon": "📚", "colors": [(220, 230, 245), (180, 200, 230)], "prompt": "classroom"},
    6: {"name": "户外自然", "icon": "🌳", "colors": [(100, 150, 200), (140, 190, 220)], "prompt": "outdoor park"},
    7: {"name": "科技感", "icon": "🔮", "colors": [(25, 20, 60), (60, 50, 100)], "prompt": "futuristic tech"}
}


class PreviewService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=120.0)
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "previews"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def get_scene_config(self, scene_id: int) -> dict:
        return SCENE_CONFIGS.get(scene_id, SCENE_CONFIGS[1])

    def get_scene_background(self, scene_id: int) -> str:
        # Apple 风格的浅色场景背景
        configs = {
            1: "linear-gradient(180deg, #F5F5F7 0%, #E8E8ED 100%)",
            2: "linear-gradient(180deg, #FFFFFF 0%, #F0F0F5 100%)",
            3: "linear-gradient(180deg, #1D1D1F 0%, #2D2D2F 100%)",  # 深色演播室
            4: "linear-gradient(180deg, #F0F0F5 0%, #E5E5EA 100%)",
            5: "linear-gradient(180deg, #FFFFFF 0%, #F8F8FA 100%)",
            6: "linear-gradient(180deg, #E8F4FD 0%, #D0E8F5 100%)",
            7: "linear-gradient(180deg, #2D2D3A 0%, #1D1D25 100%)"   # 深色科技感
        }
        return configs.get(scene_id, configs[1])

    def get_scene_icon(self, scene_id: int) -> str:
        return self.get_scene_config(scene_id).get("icon", "🏢")

    def get_scene_name(self, scene_id: int) -> str:
        return self.get_scene_config(scene_id).get("name", "默认场景")

    async def generate_preview_with_avatar(
        self,
        avatar_url: str,
        avatar_id: int,
        scene_id: int,
        api_key: str = None
    ) -> Tuple[bool, str, str]:
        """
        基于数字人模板图像生成播报预览图
        使用图片合成方式 - 确保人物与模板100%一致
        注意: MiniMax image-01 不支持真正的图生图功能
        """
        scene_config = self.get_scene_config(scene_id)

        # 下载头像图片
        avatar_image = await self._get_image(avatar_url)

        if avatar_image is None:
            logger.warning("Failed to load avatar image")
            return False, "", "无法加载头像图片"

        try:
            # 使用图片合成方式生成预览
            preview_image = self._compose_preview_image(avatar_image, scene_id)

            # 保存到本地
            import hashlib
            filename = f"preview_{scene_id}_{avatar_id}_{hashlib.md5(avatar_url.encode()).hexdigest()[:8]}.jpg"
            filepath = self.data_dir / filename

            preview_image.save(filepath, 'JPEG', quality=95)

            return True, f"http://localhost:8001/data/previews/{filename}", ""

        except Exception as e:
            logger.error(f"Preview composition error: {e}")
            return False, "", str(e)

    def _compose_preview_image(self, avatar_image: Image.Image, scene_id: int) -> Image.Image:
        """
        将头像合成到场景背景中
        使用图片叠加方式确保人物与模板100%一致
        """
        scene_config = self.get_scene_config(scene_id)
        colors = scene_config.get("colors", [(30, 35, 60), (20, 40, 80)])

        # 创建场景背景
        width, height = 1024, 1024
        background = Image.new('RGB', (width, height), colors[0])

        # 添加渐变效果
        for y in range(height):
            ratio = y / height
            r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
            for x in range(width):
                background.putpixel((x, y), (r, g, b))

        # 添加场景装饰元素
        draw = ImageDraw.Draw(background)
        self._add_scene_decorations(draw, scene_id, width, height)

        # 调整头像大小 (占画面50%)
        avatar_size = int(width * 0.55)
        avatar = avatar_image.copy()
        if avatar.mode != 'RGBA':
            avatar = avatar.convert('RGBA')

        avatar = avatar.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)

        # 居中放置头像
        x = (width - avatar_size) // 2
        y = (height - avatar_size) // 2 + 20

        # 粘贴头像 (使用透明通道)
        background.paste(avatar, (x, y), avatar)

        # 转换回RGB (去除透明通道)
        if background.mode == 'RGBA':
            background = background.convert('RGB')

        return background

    def _add_scene_decorations(self, draw: ImageDraw.Draw, scene_id: int, width: int, height: int):
        """为场景添加装饰元素"""
        scene_config = self.get_scene_config(scene_id)
        scene_name = scene_config.get("name", "")

        # 添加底部渐变遮罩 (使人物更突出)
        for i in range(50):
            alpha = int(255 * (1 - i / 50))
            y = height - 50 + i
            draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha), width=1)

        # 添加顶部标题栏
        draw.rectangle([20, 20, 280, 60], fill=(0, 0, 0, 150))
        # 场景名称会通过HTML显示，这里只是装饰

    async def _get_image(self, url: str) -> Optional[Image.Image]:
        """下载图片并返回 PIL Image 对象"""
        try:
            if url.startswith("/data/"):
                file_path = Path(__file__).parent.parent.parent / url.lstrip("/")
                if file_path.exists():
                    return Image.open(file_path)
            elif url.startswith("http://") or url.startswith("https://"):
                response = await self.client.get(url, timeout=30.0)
                if response.status_code == 200:
                    return Image.open(BytesIO(response.content))
        except Exception as e:
            logger.warning(f"Failed to load image: {e}")
        return None

    def generate_preview_html(
        self,
        avatar_url: str,
        scene_id: int,
        preview_image_url: str = None
    ) -> str:
        """生成预览 HTML"""
        background = self.get_scene_background(scene_id)
        scene_icon = self.get_scene_icon(scene_id)
        scene_name = self.get_scene_name(scene_id)

        if preview_image_url:
            return f'''
<div style="width:100%;height:100%;min-height:220px;border-radius:12px;overflow:hidden;position:relative;background:{background};">
    <img src="{preview_image_url}" style="width:100%;height:100%;object-fit:cover;" alt="预览" />
    <div style="position:absolute;bottom:10px;left:10px;background:rgba(0,0,0,0.7);padding:4px 12px;border-radius:20px;font-size:11px;color:white;">
        {scene_icon} AI 播报预览
    </div>
</div>'''

        return f'''
<div style="width:100%;height:100%;min-height:220px;background:{background};border-radius:12px;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;">
    <div style="position:absolute;inset:0;background:linear-gradient(135deg,rgba(255,255,255,0.05) 0%,transparent 50%);"></div>
    <div style="position:relative;z-index:1;display:flex;flex-direction:column;align-items:center;">
        <img src="{avatar_url}" style="width:55%;max-width:160px;border-radius:12px;box-shadow:0 15px 40px rgba(0,0,0,0.3);" alt="数字人" />
        <div style="margin-top:12px;padding:6px 16px;background:rgba(255,255,255,0.1);border-radius:20px;font-size:12px;color:white;backdrop-filter:blur(10px);">
            点击"生成预览"生成播报图
        </div>
    </div>
    <div style="position:absolute;top:10px;right:10px;background:rgba(0,0,0,0.5);padding:4px 10px;border-radius:15px;font-size:11px;color:white;">
        {scene_icon} {scene_name}
    </div>
</div>'''

    async def close(self):
        await self.client.aclose()


preview_service = PreviewService()
