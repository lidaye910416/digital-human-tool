from typing import Dict, Any, Optional
import logging
import hashlib
import httpx
import random
import os
from pathlib import Path
from sqlalchemy.orm import Session
from src.services.minimax_client import get_minimax_client
from src.services.prompt_service import prompt_service
from src.models.avatar import Avatar

logger = logging.getLogger(__name__)

# 服务器基础URL
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8001")

class AvatarService:
    def __init__(self):
        self.minimax = get_minimax_client()
        self.client = httpx.AsyncClient(timeout=60.0)
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "avatars"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_ai_avatar(
        self,
        db: Session,
        user_id: int,
        gender: str = "female",
        age: str = "young",
        style: str = "professional",
        custom_prompt: str = None
    ) -> Avatar:
        """使用 AI 生成数字人形象 - 东方人面孔"""
        logger.info(f"Generating AI avatar for user {user_id}: gender={gender}, age={age}, style={style}")
        
        seed = random.randint(1, 999999)
        
        if custom_prompt:
            result = prompt_service.process_prompt(custom_prompt, gender, age, style, seed)
            if not result["valid"]:
                raise ValueError(result["error"])
            prompt = result["optimized_prompt"]
        else:
            prompt = self._generate_asian_prompt(gender, age, style, seed)
        
        # 尝试使用 MiniMax 图像生成 API
        image_url = None
        try:
            logger.info(f"Calling MiniMax image generation...")
            response = await self.client.post(
                "https://api.minimaxi.com/v1/image_generation",
                headers={
                    "Authorization": f"Bearer {self.minimax.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "image-01",
                    "prompt": prompt,
                    "prompt_strength": 0.7
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                result_data = response.json()
                image_urls = result_data.get("data", {}).get("image_urls", [])
                if image_urls:
                    oss_url = image_urls[0]
                    local_path = await self._download_image(oss_url, seed)
                    if local_path:
                        image_url = f"{BASE_URL}{local_path}"
        
        except Exception as e:
            logger.warning(f"MiniMax image generation failed: {e}")
        
        # 如果图像生成失败，使用亚洲风格的占位图
        if not image_url:
            image_url = self._generate_asian_placeholder(gender, age, style, seed)
        
        avatar_name = self._generate_name(gender, age, style, seed)
        
        avatar = Avatar(
            user_id=user_id,
            name=avatar_name,
            type="ai_generated",
            image_url=image_url,
            config={
                "gender": gender, 
                "age": age, 
                "style": style, 
                "prompt": prompt,
                "seed": seed,
                "custom_prompt": custom_prompt
            }
        )
        db.add(avatar)
        db.commit()
        db.refresh(avatar)
        
        logger.info(f"Avatar created: id={avatar.id}, name={avatar_name}")
        return avatar
    
    async def _download_image(self, url: str, seed: int) -> Optional[str]:
        """下载图片到本地"""
        try:
            response = await self.client.get(url, timeout=30.0)
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                ext = "jpg" if "image/jpeg" in content_type.lower() else "png"
                filename = f"avatar_{seed}.{ext}"
                filepath = self.data_dir / filename
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return f"/data/avatars/{filename}"
        except Exception as e:
            logger.warning(f"Failed to download image: {e}")
        return None
    
    def _generate_asian_placeholder(self, gender: str, age: str, style: str, seed: int) -> str:
        """生成东方人风格的占位图 - 使用 anime 风格"""
        random.seed(seed)

        # lorelei 是 anime 风格，更接近东方人面孔
        # bottts 是机器人风格，比较中性
        # thumbs 是卡通风格
        styles = ["lorelei", "bottts", "lorelei", "lorelei"]  # 优先 anime 风格
        style_choice = random.choice(styles)

        # 生成一致的 seed
        combined = f"asian-{gender}-{age}-{seed}"
        seed_hash = hashlib.md5(combined.encode()).hexdigest()[:10]

        # 背景色 - 温暖的色调
        bg_colors = ["ffd5dc", "c0aede", "d1d4f9", "ffdfbf", "e8c4a0", "a0d2db"]
        random.seed(seed + 1)
        bg = random.choice(bg_colors)
        random.seed()

        # lorelei - anime 风格，更接近东方人
        if style_choice == "lorelei":
            hair_color = random.choice(["black", "brown", "blonde"])
            return f"https://api.dicebear.com/7.x/lorelei/svg?seed={seed_hash}&backgroundColor={bg}&hair={hair_color}"
        # bottts - 中性机器人风格
        elif style_choice == "bottts":
            return f"https://api.dicebear.com/7.x/bottts/svg?seed={seed_hash}&backgroundColor={bg}"
        # 默认用 lorelei
        else:
            return f"https://api.dicebear.com/7.x/lorelei/svg?seed={seed_hash}&backgroundColor={bg}"
    
    def _generate_name(self, gender: str, age: str, style: str, seed: int) -> str:
        """生成中文名字"""
        random.seed(seed)
        
        # 东方人名字池 - 主要是中文名
        name_maps = {
            "female": {
                "young": ["小雅", "欣怡", "思琪", "雨萱", "晓燕", "思雨", "诗涵", "思琳", "语晴", "子涵", "梓萱", "诗雅"],
                "adult": ["雅婷", "思敏", "雅静", "慧妍", "雅楠", "诗婷", "思颖", "雅琴", "慧敏", "雅琳"],
                "middle": ["雅芳", "雅芝", "雅慧", "雅云", "雅珍", "雅华", "雅玲", "雅娟", "雅萍", "雅红"]
            },
            "male": {
                "young": ["浩然", "子轩", "明远", "志远", "思远", "宇航", "宇轩", "俊杰", "子豪", "天宇", "浩然", "晨曦"],
                "adult": ["建伟", "志明", "文博", "志强", "伟明", "文华", "志刚", "伟强", "文杰", "志浩"],
                "middle": ["国华", "建国", "建华", "国平", "国栋", "国强", "家辉", "光辉", "光明", "广志"]
            }
        }
        
        style_cn = {
            "professional": "职业",
            "business": "商务", 
            "friendly": "亲和",
            "casual": "休闲"
        }.get(style, style)
        
        names = name_maps.get(gender, name_maps["female"]).get(age, name_maps["female"]["young"])
        name = random.choice(names)
        
        random.seed()
        return f"{name}-{style_cn}"
    
    def _generate_asian_prompt(
        self, 
        gender: str, 
        age: str, 
        style: str,
        seed: int
    ) -> str:
        """生成东方人面孔的提示词"""
        random.seed(seed)
        
        # 东方人特征描述 - 明确指定亚洲面孔
        gender_desc = {
            "female": [
                "beautiful East Asian woman", "elegant Asian lady", "attractive Chinese woman",
                "professional Asian woman", "stylish East Asian female", "graceful Asian woman",
                "charming Chinese woman", "sophisticated Asian woman", "friendly Asian lady"
            ],
            "male": [
                "handsome East Asian man", "elegant Asian gentleman", "professional Asian man",
                "stylish Chinese man", "distinguished Asian man", "charming East Asian man",
                "sophisticated Chinese man", "friendly Asian gentleman", "attractive Asian man"
            ]
        }
        
        # 年龄描述
        age_desc = {
            "young": "22-28 years old",
            "adult": "30-38 years old", 
            "middle": "45-52 years old"
        }
        
        # 亚洲人发色 - 以黑色系为主
        hair_colors = ["black hair", "dark brown hair", "chestnut brown hair", "soft black hair"]
        hair_styles = {
            "female": ["long straight hair", "shoulder length hair", "elegant bun hairstyle", "flowing black hair", "neat bob haircut", "low ponytail"],
            "male": ["short neat hair", "modern short haircut", "clean side part hair", "sleek short hair", "tidy crew cut"]
        }
        
        # 面部特征 - 适合亚洲面孔
        facial_features = ["friendly warm smile", "gentle expression", "natural approachable look", "professional confident smile", "serene friendly face"]
        
        # 服装风格
        outfits = {
            "professional": ["professional business suit", "elegant blazer with dress", "formal office attire", "sophisticated business wear"],
            "business": ["executive business suit", "corporate formal attire", "professional dress shirt", "executive business attire"],
            "friendly": ["smart casual outfit", "relaxed professional attire", "approachable casual professional", "warm welcoming outfit"],
            "casual": ["casual elegant outfit", "smart casual attire", "relaxed stylish clothing", "modern casual wear"]
        }
        
        # 场景
        scenes = {
            "professional": "modern clean office background, professional setting",
            "business": "corporate boardroom background, business environment",
            "friendly": "warm welcoming environment, approachable setting",
            "casual": "modern relaxed cafe background, contemporary setting"
        }
        
        # 选择组合
        gender_variant = random.choice(gender_desc.get(gender, gender_desc["female"]))
        age_value = age_desc.get(age, age_desc["young"])
        hair_color = random.choice(hair_colors)
        hair_style = random.choice(hair_styles.get(gender, hair_styles["female"]))
        facial = random.choice(facial_features)
        outfit = random.choice(outfits.get(style, outfits["professional"]))
        scene = scenes.get(style, scenes["professional"])
        
        # 构建提示词 - 强调亚洲面孔
        prompt = f"A {age_value} {gender_variant} with East Asian features, {hair_color}, {hair_style}, {facial}, wearing {outfit}, {scene}, high quality professional portrait photography, natural studio lighting, sharp focus, detailed skin texture, realistic, authentic Asian appearance"
        
        random.seed()
        return prompt
    
    async def create_photo_avatar(
        self,
        db: Session,
        user_id: int,
        photo_url: str,
        name: str = "Photo Avatar"
    ) -> Avatar:
        """从照片创建数字人形象"""
        logger.info(f"Creating photo avatar for user {user_id}")
        
        local_url = photo_url
        try:
            seed = random.randint(1, 999999)
            local_path = await self._download_image(photo_url, seed)
            if local_path:
                local_url = f"{BASE_URL}{local_path}"
        except Exception as e:
            logger.warning(f"Failed to download photo: {e}")
        
        avatar = Avatar(
            user_id=user_id,
            name=name,
            type="photo_driven",
            image_url=local_url,
            config={"source": "upload"}
        )
        db.add(avatar)
        db.commit()
        db.refresh(avatar)
        
        return avatar

    def calculate_avatar_credits(self, avatar_type: str) -> int:
        if avatar_type == "ai_generated":
            return 5
        elif avatar_type == "photo_driven":
            return 3
        return 0

    def get_avatar_list(self, db: Session, user_id: int) -> list:
        avatars = db.query(Avatar).filter(Avatar.user_id == user_id).order_by(Avatar.id.desc()).all()
        result = []
        for a in avatars:
            image_url = a.image_url or ""
            if image_url.startswith('/data/'):
                image_url = f"{BASE_URL}{image_url}"
            
            result.append({
                "id": a.id,
                "name": a.name,
                "type": a.type,
                "image_url": image_url,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "config": a.config
            })
        return result

    async def close(self):
        await self.client.aclose()
