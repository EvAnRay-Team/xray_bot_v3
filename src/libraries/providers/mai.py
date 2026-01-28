from .base_client import BaseClient
from typing import Optional, List
import nonebot
from nonebot.log import logger
config = nonebot.get_driver().config

class DivingFishMaiApi(BaseClient):
    def __init__(self):
        base_url = 'https://www.diving-fish.com/api/maimaidxprober'
        divingfish_developer_token = getattr(config,"divingfish_developer_token")
        headers = {"developer-token": divingfish_developer_token}
        super().__init__(base_url=base_url, headers=headers)
        
    async def dev_player_record(self, user_id: int, music_id_list: Optional[List[str]]):
        payload :dict = {"qq":user_id}
        payload['music_id'] = music_id_list
        logger.info(f'post start,payload: {payload},endpoint: /dev/player/record')
        resp = await self.client.post(f"/dev/player/record", json=payload)
        logger.info(f'post end,status_code: {resp.status_code}')
        resp.raise_for_status()
        return resp.json()
    
    async def music_data(self):
        resp = await self.client.get("/music_data")
        resp.raise_for_status()
        return resp.json()
    
class LxnsMaiApi(BaseClient):
    def __init__(self):
        base_url = 'https://maimai.lxns.net/api/v0'
        lxns_developer_token = getattr(config,"lxns_developer_token")
        headers = {"Authorization": lxns_developer_token}
        super().__init__(base_url=base_url, headers=headers)

    async def song_list(self):
        resp = await self.client.get(f"/maimai/song/list")
        resp.raise_for_status()
        return resp.json()