from pathlib import Path
from typing import Optional
from nonebot.log import logger
from src.libraries.tools.execution_time import timing_decorator_async, timing_block
from src.libraries.providers.assets_tencent_cos import assets_tencent_cos_client
from src.libraries.config import GLOBAL_PATH
from src.libraries.schemas.mai_music import MaiMusic
from sqlalchemy import select
from src.libraries.models import Abstract
from nonebot_plugin_orm import get_session
import random

@timing_decorator_async
async def get_cover_file_path(music_id: int, is_abstract: bool = True):
    if is_abstract:
        with timing_block("SQL 查询"):
            async with get_session() as session:
                # 构造查询
                stmt = select(Abstract).where(Abstract.music_id == music_id)
                result = await session.execute(stmt)
                abstracts = result.scalars().all()

        if not abstracts:
            return await get_normal_cover_file_path(music_id), '未收录'

        abstract = random.choice(abstracts)
        logger.info(f"abstract cover info {abstract}")
        return get_abstract_cover_file_path(abstract.file_key), abstract.nickname
    else:
        return await get_normal_cover_file_path(music_id), '-'

async def get_normal_cover_file_path(music_id: int, base_path: str = GLOBAL_PATH.NORMAL_COVER_PATH) -> Optional[Path]:
    """
    获取普通封面路径,优先从本地获取,不存在则从远程下载
    
    Args:
        music_id: 音乐 ID
        base_path: 本地存储基础路径
    
    Returns:
        Optional[Path]: 图片路径,如果获取失败抛出 FileNotFoundError
    """
    from src.libraries.providers.assets import lxns_assets_client
    
    local_path = Path(base_path) / f"{music_id}.png"
    
    # 检查本地文件是否存在
    if local_path.exists():
        logger.debug(f"从本地获取封面: {local_path}")
        return local_path
    
    # 本地不存在,尝试从远程下载
    logger.info(f"本地封面不存在,尝试从远程下载: {music_id}")

    # 落雪资源下载

    if await lxns_assets_client.download_cover(music_id, local_path):
        return local_path
    
    # 水鱼资源下载
    
    raise FileNotFoundError(f"封面获取失败: {music_id}")
    # logger.error(f"封面获取失败: {music_id}")
    # return None


def get_abstract_cover_file_path(key: str, base_path: str = GLOBAL_PATH.ABSTRACT_COVER_PATH) -> Optional[Path]:
    """
    获取图片路径,优先从本地获取,不存在则从 COS 下载
    
    Args:
        key: 文件键 (例如: maimaidx/abstract_cover/12/34/md5.png)
        base_path: 本地存储基础路径
    
    Returns:
        Optional[Path]: 图片路径,如果获取失败返回 None
    """

    file_name = key.split('/')[-1]
    local_path = Path(base_path) / file_name
    
    # 检查本地文件是否存在
    if local_path.exists():
        logger.debug(f"从本地获取图片: {local_path}")
        return local_path
    
    # 本地不存在,尝试从 COS 下载
    logger.info(f"本地文件不存在,尝试从 COS 下载: {key}")
    if assets_tencent_cos_client.download_file(key, local_path):
        return local_path
    
    raise FileNotFoundError(f"文件 {key} 不存在于本地或 COS")


def truncate_text(text, font, max_width):
    if font.getsize(text)[0] <= max_width:
        return text
    else:
        for i in range(len(text), 0, -1):
            if font.getsize(text[:i] + '...')[0] <= max_width:
                return text[:i] + '...'
        return '...'
    
def decimalPoints(num,count):
    num = str(int(round(num * 10**count,8)) / 10**count)  
    if '.0' == num[-2:]:
        num += ('0'* (count-1-(len(num.split('.')[1]))))
    if len(num.split('.')[1]) < count:
        num += ('0'* (count-(len(num.split('.')[1]))))
    return num
