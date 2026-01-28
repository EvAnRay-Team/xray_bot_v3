"""
Mai 相关的请求层，负责调用 API 并将响应转换为实体对象
"""
from typing import Optional, List, Dict
from src.libraries.providers.mai import DivingFishMaiApi
from src.libraries.schemas.mai_record import MaiRecordList, DivingFishMaiRecord
from nonebot.log import logger


class MaiRequestService:
    """Mai 请求服务，负责 API 调用和响应实体化"""
    
    def __init__(self):
        self.api = DivingFishMaiApi()
    
    async def get_player_record(
        self, 
        user_id: int, 
        music_id_list: Optional[List[str]] = None
    ) -> MaiRecordList:
        """
        获取玩家记录并实体化为 MaiRecord 对象
        
        Args:
            user_id: 用户 ID
            music_id_list: 音乐 ID 列表，可选
            
        Returns:
            MaiRecordList: 包含所有 MaiRecord 的列表
        """
        # 调用 API 获取原始数据
        # API 返回格式: Dict[str, List[dict]]，其中 key 是歌曲ID，value 是该歌曲的所有难度记录列表
        raw_data: Dict[str, List[dict]] = await self.api.dev_player_record(user_id, music_id_list)

        result = []

        # 遍历所有歌曲的所有记录
        for song_id_str, records_list in raw_data.items():
            if not isinstance(records_list, list):
                logger.warning(f"Unexpected record format for song {song_id_str}: {type(records_list)}")
                continue
            
            for record_data in records_list:
                try:
                    # 解析 DivingFish 格式的记录
                    df_record = DivingFishMaiRecord.model_validate(record_data)
                    
                    # 转换为 MaiRecord（会自动从 total_music 中查找完整的音乐信息）
                    mai_record = df_record.to_mai_record()
                    
                    result.append(mai_record)
                except Exception as e:
                    logger.error(
                        f"Failed to convert record for song {song_id_str}, "
                        f"level_index {record_data.get('level_index', 'unknown')}: {e}"
                    )
                    continue

        return MaiRecordList(records=result)
    
    async def get_music_data(self) -> list:
        """
        获取音乐数据
        
        Returns:
            list: 音乐数据列表
        """
        return await self.api.music_data()

