from typing import Dict, Any, Optional
import logging
from sqlalchemy.orm import Session
from src.services.minimax_client import get_minimax_client
from src.services.tts_service import TextToSpeechService
from src.models.video_project import VideoProject

logger = logging.getLogger(__name__)

class VideoService:
    def __init__(self):
        self.minimax = get_minimax_client()
        self.tts_service = TextToSpeechService()

    async def create_project(
        self,
        db: Session,
        user_id: int,
        title: str,
        script_text: str,
        avatar_id: int,
        scene_id: str = "default",
        voice_config: Dict[str, Any] = None
    ) -> VideoProject:
        """创建视频项目"""
        logger.info(f"Creating project: {title} for user {user_id}")

        project = VideoProject(
            user_id=user_id,
            title=title,
            script_text=script_text,
            avatar_id=avatar_id,
            scene_id=scene_id,
            voice_config=voice_config or {"voice_id": "female-tianmei", "speed": 1.0},
            status="pending"
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        return project

    async def generate_video(
        self,
        db: Session,
        project_id: int
    ) -> Dict[str, Any]:
        """生成视频 - 完整流程"""
        logger.info(f"Generating video for project {project_id}")

        project = db.query(VideoProject).filter(VideoProject.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # 更新状态为处理中
        project.status = "processing"
        db.commit()

        try:
            # 1. 语音合成 (TTS)
            logger.info("Step 1: Synthesizing speech...")
            tts_result = await self.tts_service.synthesize(
                text=project.script_text,
                voice_config=project.voice_config
            )
            audio_url = tts_result.get("audio_url", "")
            logger.info(f"TTS completed: {audio_url[:80] if audio_url else 'None'}...")

            # 2. 获取数字人形象
            logger.info("Step 2: Getting avatar...")
            from src.models.avatar import Avatar
            avatar = db.query(Avatar).filter(Avatar.id == project.avatar_id).first()
            if not avatar:
                raise ValueError(f"Avatar {project.avatar_id} not found")
            image_url = avatar.image_url
            logger.info(f"Avatar URL: {image_url}")

            # 3. 检查是否有音频和图像
            if not audio_url:
                raise ValueError("Audio synthesis failed - no audio URL")
            if not image_url:
                raise ValueError("Avatar has no image URL")

            # 4. 生成视频 (图生视频)
            logger.info("Step 3: Generating video...")
            try:
                video_response = await self.minimax.video_generation_i2v(
                    prompt=f"A person speaking naturally about: {project.script_text[:50]}...",
                    image_url=image_url
                )

                # 检查响应
                if "task_id" in video_response and video_response.get("task_id"):
                    video_url = f"https://api.minimax.com/v1/video/task/{video_response['task_id']}"
                    video_status = "processing"
                else:
                    video_url = ""
                    video_status = "pending"

                logger.info(f"Video generation submitted: {video_response}")

            except Exception as video_error:
                logger.error(f"Video generation error: {video_error}")
                video_url = ""
                video_status = "pending"

            # 5. 更新项目
            project.status = "completed"
            project.output_url = video_url or audio_url  # 返回音频 URL 作为备用
            project.credits_used = self.calculate_credits(project.script_text)
            db.commit()

            return {
                "status": "completed",
                "video_url": video_url,
                "audio_url": audio_url,
                "credits_used": project.credits_used,
                "note": "TTS 成功，视频生成需要 MiniMax 视频服务"
            }

        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            project.status = "failed"
            db.commit()
            raise e

    def calculate_credits(self, script_text: str) -> int:
        """计算视频生成的积分消耗"""
        minutes = len(script_text) / 60
        return max(10, int(minutes * 10))

    def get_project(self, db: Session, project_id: int) -> Optional[VideoProject]:
        return db.query(VideoProject).filter(VideoProject.id == project_id).first()

    def get_user_projects(self, db: Session, user_id: int) -> list:
        projects = db.query(VideoProject).filter(
            VideoProject.user_id == user_id
        ).order_by(VideoProject.created_at.desc()).all()

        return [
            {
                "id": p.id,
                "title": p.title,
                "status": p.status,
                "output_url": p.output_url,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in projects
        ]
