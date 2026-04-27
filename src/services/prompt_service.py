"""
提示词处理服务 - 东方人面孔优化
"""
import re
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class PromptService:
    # 不合适的关键词
    INAPPROPRIATE_PATTERNS = {
        "explicit": [
            r"nude", r"naked", r"sexy", r"sexual", r"erotic", r"porn", r"xxx",
            r"暴露", r"色情", r"性感", r"裸体", r"情色", r"勾引", r"诱惑"
        ],
        "violence": [
            r"blood", r"gore", r"violent", r"weapon", r"knife", r"gun",
            r"血腥", r"暴力", r"武器", r"杀人", r"死亡"
        ],
        "political": [
            r"politician", r"president", r"government.*flag",
            r"国家领导人", r"总统", r"主席"
        ],
        "discrimination": [
            r"hate", r"racist", r"discrimination", r"nazi",
            r"歧视", r"种族歧视", r"仇恨"
        ]
    }
    
    def validate_prompt(self, prompt: str) -> Tuple[bool, str, Optional[str]]:
        """验证提示词"""
        if not prompt or not prompt.strip():
            return False, "", "提示词不能为空"
        
        prompt = prompt.strip()
        
        for category, patterns in self.INAPPROPRIATE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, prompt, re.IGNORECASE):
                    return False, "", self._get_category_message(category)
        
        return True, prompt, None
    
    def _get_category_message(self, category: str) -> str:
        messages = {
            "explicit": "⚠️ 提示词包含不适当内容",
            "violence": "⚠️ 提示词包含暴力内容",
            "political": "⚠️ 提示词包含敏感内容",
            "discrimination": "⚠️ 提示词包含歧视内容"
        }
        return messages.get(category, "⚠️ 提示词不合适")
    
    def process_prompt(
        self,
        user_prompt: str,
        gender: str = "female",
        age: str = "young",
        style: str = "professional",
        seed: int = None
    ) -> dict:
        """处理提示词，转换为东方人面孔"""
        is_valid, sanitized, error = self.validate_prompt(user_prompt)
        
        if not is_valid:
            return {
                "valid": False,
                "original_prompt": user_prompt,
                "optimized_prompt": "",
                "detected_params": {},
                "error": error
            }
        
        # 转换为东方人面孔的提示词
        optimized = self._convert_to_asian_prompt(sanitized, gender, age, style, seed)
        
        return {
            "valid": True,
            "original_prompt": user_prompt,
            "optimized_prompt": optimized,
            "detected_params": {"gender": gender, "age": age, "style": style},
            "error": None
        }
    
    def _convert_to_asian_prompt(
        self,
        user_prompt: str,
        gender: str,
        age: str,
        style: str,
        seed: int
    ) -> str:
        """将用户提示词转换为东方人面孔的英文提示词"""
        import random
        if seed:
            random.seed(seed)
        else:
            random.seed()
        
        prompt_lower = user_prompt.lower()
        
        # 性别描述
        gender_desc = {
            "female": random.choice([
                "beautiful East Asian woman", "elegant Asian lady", "attractive Chinese woman",
                "professional Asian woman", "stylish East Asian female", "graceful Asian woman"
            ]),
            "male": random.choice([
                "handsome East Asian man", "elegant Asian gentleman", "professional Asian man",
                "stylish Chinese man", "distinguished Asian man", "attractive Asian man"
            ])
        }
        gender_variant = gender_desc.get(gender, gender_desc["female"])
        
        # 年龄
        age_desc = {
            "young": "22-28 years old",
            "adult": "30-38 years old",
            "middle": "45-52 years old"
        }
        age_value = age_desc.get(age, age_desc["young"])
        
        # 发型 - 从用户描述中提取
        hair_features = self._extract_hair_feature(prompt_lower)
        
        # 面部特征
        face_features = self._extract_face_feature(prompt_lower)
        
        # 服装
        outfit = self._extract_outfit(prompt_lower, style)
        
        # 风格场景
        scene = self._get_scene(style)
        
        # 构建最终提示词
        parts = [f"A {age_value} {gender_variant}"]
        
        if hair_features:
            parts.append(hair_features)
        else:
            # 默认亚洲人特征
            parts.append("black hair")
            if gender == "female":
                parts.append(random.choice(["long straight hair", "shoulder length hair"]))
            else:
                parts.append("short neat hair")
        
        if face_features:
            parts.append(face_features)
        else:
            parts.append("friendly warm expression")
        
        if outfit:
            parts.append(outfit)
        
        parts.append(scene)
        parts.extend([
            "high quality professional portrait",
            "natural soft lighting",
            "sharp focus, detailed skin texture",
            "realistic, authentic East Asian appearance"
        ])
        
        random.seed()
        return ", ".join(parts)
    
    def _extract_hair_feature(self, prompt: str) -> str:
        """提取发型特征"""
        hair_map = {
            "长发": "long straight black hair",
            "短发": "short hair",
            "卷发": "soft curly hair",
            "直发": "straight hair",
            "马尾": "tied hair with ponytail",
            "丸子头": "elegant bun hairstyle",
            "波浪": "wavy hair",
            "黑发": "black hair",
            "棕色": "brown hair"
        }
        for cn, en in hair_map.items():
            if cn in prompt:
                return en
        return ""
    
    def _extract_face_feature(self, prompt: str) -> str:
        """提取面部特征"""
        face_map = {
            "眼镜": "wearing glasses",
            "微笑": "friendly smile",
            "笑脸": "warm smile",
            "严肃": "serious professional expression",
            "亲和": "approachable friendly expression",
            "成熟": "mature dignified expression"
        }
        for cn, en in face_map.items():
            if cn in prompt:
                return en
        return ""
    
    def _extract_outfit(self, prompt: str, style: str) -> str:
        """提取服装特征"""
        outfit_map = {
            "西装": "wearing business suit",
            "正装": "formal attire",
            "休闲": "casual smart outfit",
            "衬衫": "wearing dress shirt",
            "T恤": "casual t-shirt",
            "裙子": "wearing skirt",
            "连衣裙": "wearing dress"
        }
        for cn, en in outfit_map.items():
            if cn in prompt:
                return en
        
        # 默认风格服装
        default_outfits = {
            "professional": "wearing professional business attire",
            "business": "wearing executive business suit",
            "friendly": "wearing approachable smart casual outfit",
            "casual": "wearing casual elegant outfit"
        }
        return default_outfits.get(style, default_outfits["professional"])
    
    def _get_scene(self, style: str) -> str:
        """获取场景描述"""
        scenes = {
            "professional": "modern professional office background",
            "business": "corporate business environment",
            "friendly": "warm welcoming environment",
            "casual": "modern relaxed setting"
        }
        return scenes.get(style, scenes["professional"])


prompt_service = PromptService()
