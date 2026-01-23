
import random
from typing import Dict, Any, Optional
from src.libraries.config.GLOBAL_PATH import (
    NORMAL_COVER_PATH, ABSTRACT_COVER_PATH
)
from src.libraries.config.tarot.tarot_constants import (
    MAJOR_ARCANA, TAROT_IMAGE_MAPPING, 
    TAROT_UPRIGHT_MEANING, TAROT_REVERSED_MEANING
)
from src.libraries.transformers.maimaidx.music_transformer import transform_music_data

# Global cache for music data to avoid reloading on every request
_MUSIC_DATA_CACHE = None
_MUSIC_ID_MAP_CACHE = None

def _get_music_map():
    global _MUSIC_DATA_CACHE, _MUSIC_ID_MAP_CACHE
    if _MUSIC_DATA_CACHE is None:
        _MUSIC_DATA_CACHE = transform_music_data()
        _MUSIC_ID_MAP_CACHE = {str(song['id']): song for song in _MUSIC_DATA_CACHE}
    return _MUSIC_ID_MAP_CACHE

def tarot_divination(bind_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    塔罗牌占卜主逻辑
    :param bind_data: 可选的绑定数据 {'card_name': str, 'position': bool}，用于指定抽卡结果
    :return: 包含占卜结果、歌曲信息、图片路径的字典
    """
    if bind_data:
        card_name = bind_data["card_name"]
        is_upright = bind_data["position"]
    else:
        card_name = random.choice(MAJOR_ARCANA)
        is_upright = random.choice([True, False])
    
    # 1. 确定牌义
    if is_upright:
        upright_info = "正位"
        meaning = TAROT_UPRIGHT_MEANING.get(card_name, "")
    else:
        upright_info = "逆位"
        meaning = TAROT_REVERSED_MEANING.get(card_name, "")

    # 2. 确定关联歌曲 ID
    possible_images = TAROT_IMAGE_MAPPING.get(card_name, [])
    if not possible_images:
        image_id = "100" # fallback
    else:
        image_id = str(random.choice(possible_images))

    # 3. 获取歌曲详情
    music_map = _get_music_map()
    raw_music = music_map.get(image_id)
    
    if raw_music:
        music_title = raw_music['title']
        music_artist = raw_music['basic_info']['artist']
        
        # 4. 确定封面路径
        # 简单逻辑：假定抽象画存在（实际应检查文件是否存在）
        # 这里仅生成路径字符串，实际文件读取交由 drawer 处理
        image_path_abstract = f'{ABSTRACT_COVER_PATH}/{image_id}.png'
        image_path_normal = f'{NORMAL_COVER_PATH}/{image_id}.png'
    else:
        music_title = "Unknown"
        music_artist = "Unknown"
        image_path_abstract = f'{NORMAL_COVER_PATH}/1000.png'
        image_path_normal = f'{NORMAL_COVER_PATH}/1000.png'

    return {
        "tarot_name": card_name,
        "tarot_upright": upright_info,
        "tarot_meaning": meaning,
        "id": image_id,
        "title": music_title,
        "artist": music_artist,
        "cover_abstract": image_path_abstract,
        "cover_normal": image_path_normal
    }
