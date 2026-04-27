from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import os
import logging
from src.models.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])

# 服务器基础URL
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8001")

# ============ Request Models ============
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class CreateProjectRequest(BaseModel):
    title: str
    script_text: str
    avatar_id: int
    scene_id: str = "default"
    user_id: int = 1
    voice_config: Optional[dict] = None

class GenerateSceneRequest(BaseModel):
    prompt: str
    category: str = "custom"
    user_id: int = 1

class CreateAvatarRequest(BaseModel):
    photo_url: str
    name: str = "Photo Avatar"
    user_id: int = 1

# ============ User Endpoints ============
@router.post("/users/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    from src.services.user_service import create_user
    try:
        user = create_user(db, user_data.username, user_data.email, user_data.password)
        return {"id": user.id, "username": user.username, "email": user.email, "credits": user.credits}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/users/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    from src.services.user_service import authenticate_user
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"user_id": user.id, "username": user.username, "credits": user.credits}

# ============ Avatar Endpoints ============
class GenerateAvatarRequest(BaseModel):
    user_id: int = 1
    gender: str = "female"
    age: str = "young"
    style: str = "professional"
    custom_prompt: Optional[str] = None

@router.post("/avatars/generate-ai")
async def generate_ai_avatar(
    request: GenerateAvatarRequest,
    db: Session = Depends(get_db)
):
    """生成AI数字人，支持自定义提示词"""
    from src.services.avatar_service import AvatarService
    service = AvatarService()
    avatar = await service.generate_ai_avatar(
        db,
        request.user_id,
        request.gender,
        request.age,
        request.style,
        request.custom_prompt
    )
    return {
        "id": avatar.id,
        "name": avatar.name,
        "image_url": avatar.image_url,
        "type": avatar.type,
        "config": avatar.config
    }

@router.post("/avatars/validate-prompt")
async def validate_prompt(
    prompt: str = Body(...),
    gender: str = Body("female"),
    age: str = Body("young"),
    style: str = Body("professional")
):
    """验证并优化用户提示词"""
    from src.services.prompt_service import prompt_service
    result = prompt_service.process_prompt(prompt, gender, age, style)
    return result

@router.post("/avatars/from-photo")
async def create_photo_avatar(
    request: CreateAvatarRequest,
    db: Session = Depends(get_db)
):
    from src.services.avatar_service import AvatarService
    service = AvatarService()
    avatar = await service.create_photo_avatar(db, request.user_id, request.photo_url, request.name)
    return {"id": avatar.id, "image_url": avatar.image_url, "type": avatar.type}

@router.get("/avatars")
async def get_avatars(user_id: int = Query(1), db: Session = Depends(get_db)):
    from src.services.avatar_service import AvatarService
    service = AvatarService()
    return service.get_avatar_list(db, user_id)

# ============ Scene Endpoints ============
@router.get("/scenes")
async def get_scenes(category: Optional[str] = Query(None), db: Session = Depends(get_db)):
    from src.services.scene_service import SceneService
    service = SceneService()
    if category:
        return service.get_scenes_by_category(db, category)
    return service.get_all_scenes(db)

@router.get("/scenes/presets")
async def get_scene_presets():
    from src.services.scene_generator import SceneGenerator
    generator = SceneGenerator()
    return generator.get_scene_presets()

@router.get("/scenes/{scene_id}")
async def get_scene(scene_id: int, db: Session = Depends(get_db)):
    from src.services.scene_service import SceneService
    service = SceneService()
    scene = service.get_scene_by_id(db, scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    return scene

@router.get("/preview")
async def get_preview(
    avatar_id: int = Query(...),
    scene_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """获取预览 - 仅显示当前数字人和场景组合，不自动生成"""
    from src.services.preview_service import preview_service
    from src.models.avatar import Avatar
    from src.services.scene_service import SceneService

    # 获取数字人
    avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")

    # 构建头像 URL
    avatar_url = avatar.image_url or ""
    if avatar_url.startswith('/data/'):
        avatar_url = f"{BASE_URL}{avatar_url}"

    # 获取场景
    scene_service = SceneService()
    scene = scene_service.get_scene_by_id(db, scene_id)

    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    # 生成预览 HTML（不自动生成 AI 预览图）
    preview_html = preview_service.generate_preview_html(
        avatar_url=avatar_url,
        scene_id=scene_id,
        preview_image_url=None
    )

    return {
        "preview_html": preview_html,
        "preview_image_url": None,
        "generate_status": "ready",
        "avatar": {
            "id": avatar.id,
            "name": avatar.name,
            "image_url": avatar_url,
            "type": avatar.type
        },
        "scene": scene,
        "scene_background": preview_service.get_scene_background(scene_id),
        "scene_icon": preview_service.get_scene_icon(scene_id),
        "scene_name": preview_service.get_scene_name(scene_id)
    }


@router.post("/preview/generate")
async def generate_preview(
    avatar_id: int = Query(...),
    scene_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """手动生成预览 - AI 基于数字人模板图像生成播报预览图"""
    from src.services.preview_service import preview_service
    from src.models.avatar import Avatar
    from src.config import MINIMAX_API_KEY

    if not MINIMAX_API_KEY:
        raise HTTPException(status_code=400, detail="需要配置 MiniMax API Key")

    # 获取数字人
    avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")

    # 构建头像 URL
    avatar_url = avatar.image_url or ""
    if avatar_url.startswith('/data/'):
        avatar_url = f"{BASE_URL}{avatar_url}"

    logger.info(f"Generating preview for avatar: {avatar_url}, scene: {scene_id}")

    # AI 生成预览图 - 传入 avatar_id 以便下载图片
    success, image_url, error = await preview_service.generate_preview_with_avatar(
        avatar_url=avatar_url,
        avatar_id=avatar_id,
        scene_id=scene_id,
        api_key=MINIMAX_API_KEY
    )

    if not success:
        raise HTTPException(status_code=400, detail=error or "预览生成失败")

    return {
        "success": True,
        "preview_image_url": image_url,
        "avatar_url": avatar_url,
        "scene_id": scene_id,
        "scene_icon": preview_service.get_scene_icon(scene_id),
        "scene_name": preview_service.get_scene_name(scene_id)
    }
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    return scene

@router.post("/scenes/generate")
async def generate_scene(request: GenerateSceneRequest, db: Session = Depends(get_db)):
    from src.services.scene_generator import SceneGenerator
    generator = SceneGenerator()
    result = await generator.generate_scene(request.prompt, request.category)
    scene = await generator.save_generated_scene(db, request.user_id, request.prompt, result["scene_url"])
    return {"id": scene.id, "scene_url": scene.scene_url, "prompt": request.prompt}

# ============ Voice Endpoints ============
@router.get("/voices")
async def get_voices():
    from src.services.voice_config import VoiceConfigService
    service = VoiceConfigService()
    # 返回所有声音（包含可用状态）
    return {"voices": service.get_all_voices()}

@router.get("/voices/available")
async def get_available_voices():
    """获取可用的声音列表"""
    from src.services.voice_config import VoiceConfigService
    service = VoiceConfigService()
    return {"voices": service.get_available_voices()}

@router.get("/voices/presets")
async def get_voice_presets():
    from src.services.voice_config import VoiceConfigService
    service = VoiceConfigService()
    return {
        "presets": [
            {"name": "professional_female", **service.apply_preset("professional_female")},
            {"name": "professional_male", **service.apply_preset("professional_male")},
            {"name": "friendly_female", **service.apply_preset("friendly_female")},
            {"name": "friendly_male", **service.apply_preset("friendly_male")},
        ]
    }

# ============ Project Endpoints ============
@router.post("/projects")
async def create_project(request: CreateProjectRequest, db: Session = Depends(get_db)):
    from src.services.video_service import VideoService
    service = VideoService()
    project = await service.create_project(
        db, request.user_id, request.title, request.script_text, 
        request.avatar_id, request.scene_id, request.voice_config
    )
    return {"id": project.id, "title": project.title, "status": project.status}

@router.get("/projects")
async def get_user_projects(user_id: int = Query(1), db: Session = Depends(get_db)):
    from src.services.video_service import VideoService
    service = VideoService()
    return service.get_user_projects(db, user_id)

@router.get("/projects/{project_id}")
async def get_project(project_id: int, db: Session = Depends(get_db)):
    from src.services.video_service import VideoService
    service = VideoService()
    project = service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "id": project.id,
        "title": project.title,
        "status": project.status,
        "output_url": project.output_url,
        "credits_used": project.credits_used
    }

@router.post("/projects/{project_id}/generate")
async def generate_video(project_id: int, db: Session = Depends(get_db)):
    from src.services.video_service import VideoService
    service = VideoService()
    try:
        result = await service.generate_video(db, project_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============ Export Endpoints ============
@router.get("/export/{project_id}/mp4")
async def export_as_mp4(project_id: int, quality: str = Query("1080p"), db: Session = Depends(get_db)):
    from src.services.export_service import ExportService
    from src.services.video_service import VideoService
    service = VideoService()
    project = service.get_project(db, project_id)
    if not project or not project.output_url:
        raise HTTPException(status_code=404, detail="Video not found")
    export_service = ExportService()
    return export_service.export_as_mp4(project.output_url, quality)

@router.get("/export/{project_id}/gif")
async def export_as_gif(project_id: int, fps: int = Query(10), db: Session = Depends(get_db)):
    from src.services.export_service import ExportService
    from src.services.video_service import VideoService
    service = VideoService()
    project = service.get_project(db, project_id)
    if not project or not project.output_url:
        raise HTTPException(status_code=404, detail="Video not found")
    export_service = ExportService()
    return export_service.export_as_gif(project.output_url, fps)

@router.get("/share/{project_id}")
async def share_video(project_id: int, platform: str = Query("general"), db: Session = Depends(get_db)):
    from src.services.export_service import ExportService
    from src.services.video_service import VideoService
    service = VideoService()
    project = service.get_project(db, project_id)
    if not project or not project.output_url:
        raise HTTPException(status_code=404, detail="Video not found")
    export_service = ExportService()
    link = export_service.generate_share_link(project.output_url, platform)
    return {"share_url": link}

# ============ Language Endpoints ============
@router.get("/languages")
async def get_languages():
    from src.services.language_service import LanguageService
    service = LanguageService()
    return {"languages": service.get_languages()}

# ============ TTS Test Endpoint ============
@router.post("/voices/test")
async def test_tts(
    text: str = Body("测试文字转语音功能"),
    voice_id: str = Body("female-tianmei"),
    db: Session = Depends(get_db)
):
    """测试语音合成功能"""
    from src.services.minimax_client import get_minimax_client
    client = get_minimax_client()

    try:
        result = await client.text_to_speech(text, voice_id)
        return {
            "success": True,
            "voice_id": voice_id,
            "audio_url": result.get("data", {}).get("audio_url"),
            "available_voices": client.get_available_voices()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "available_voices": client.get_available_voices()
        }

# ============ Health Check ============
@router.get("/status")
async def api_status():
    from src.config import validate_config, MINIMAX_API_KEY
    from src.services.minimax_client import get_minimax_client
    from src.services.azure_tts_client import get_azure_tts_client
    import os

    errors = validate_config()

    # 检测 TTS 提供商
    azure_configured = bool(os.environ.get("AZURE_SPEECH_KEY") or os.environ.get("AZURE_TTS_KEY"))

    status = {
        "status": "ok" if not errors else "config_error",
        "minimax_api_key_set": bool(MINIMAX_API_KEY),
        "azure_tts_configured": azure_configured,
        "errors": errors,
        "minimax_api": {
            "available": False,
            "tts": {"available": False, "models": [], "error": None},
            "image": {"available": False, "error": None},
            "video": {"available": False, "error": None}
        },
        "tts_provider": "none",  # 当前使用的 TTS 提供商
        "recommendation": None
    }

    # 检查 MiniMax API 状态
    if MINIMAX_API_KEY:
        try:
            client = get_minimax_client()
            api_status = await client.check_api_status()
            status["minimax_api"] = api_status
        except Exception as e:
            status["minimax_api"]["error"] = str(e)

    # 确定 TTS 提供商
    if azure_configured:
        status["tts_provider"] = "azure"
    elif status["minimax_api"].get("tts", {}).get("available"):
        status["tts_provider"] = "minimax"
    else:
        status["tts_provider"] = "mock"
        status["recommendation"] = (
            "TTS 不可用！请选择以下方案之一：\n"
            "1. 在 MiniMax 平台启用 Text-to-Speech 模型：https://platform.minimaxi.com\n"
            "2. 配置 Azure TTS：设置 AZURE_SPEECH_KEY 和 AZURE_SPEECH_REGION 环境变量"
        )

    return status
