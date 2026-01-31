from .base_client import BaseClient
from pathlib import Path
from src.libraries.tools.execution_time import timing_decorator_async
import nonebot
from nonebot.log import logger
import httpx

config = nonebot.get_driver().config

class DivingFishAssetsClient(BaseClient):
    def __init__(self):
        base_url = 'https://www.diving-fish.com'
        super().__init__(base_url=base_url)
        

    
class LxnsAssetsClient(BaseClient):
    def __init__(self):
        base_url = 'https://assets.lxns.net'
        super().__init__(base_url=base_url)

    @timing_decorator_async
    async def download_cover(self, music_id: int, local_path: Path) -> bool:
        """
        下载封面图片并保存到本地
        
        Args:
            music_id: 音乐 ID
            local_path: 本地保存路径
        
        Returns:
            bool: 是否下载成功
        """
        try:
            #由于落雪歌曲ID机制和水鱼不一样，且项目统一使用水鱼ID机制，需要转换成落雪机制通过落雪资源获取静态资源
            if music_id > 10000:
                # 取前四位，去掉前导 0，再转为 int
                music_id = int(str(music_id)[-4:].lstrip('0') or '0')

            resp = await self.client.get(f"/maimai/jacket/{music_id}.png")
            resp.raise_for_status()
            
            # 确保父目录存在
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存文件
            with open(local_path, 'wb') as f:
                f.write(resp.content)
            
            logger.info(f"封面下载成功: {music_id} -> {local_path}")
            return True
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"封面不存在: {music_id}")
            else:
                logger.error(f"下载封面失败: {music_id}, HTTP {e.response.status_code}")
            return False
        except Exception as e:
            logger.error(f"下载封面失败: {music_id}, 错误: {e}")
            return False

# 全局客户端实例
lxns_assets_client = LxnsAssetsClient()
divingfish_assets_client = DivingFishAssetsClient()
