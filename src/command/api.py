from command.base import BaseCommand
from src.libraries.requests.mai import MaiRequestService
from nonebot.log import logger

import asyncio

class Command(BaseCommand):
    def handle(self, **options):
        try:
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            pass

    async def run_async(self):
        print("Testing BaseClient from command framework...")
        
        # 使用请求层服务
        request_service = MaiRequestService()
        
        # 获取玩家记录（自动实体化为 MaiRecord）
        dev_player_record = await request_service.get_player_record(
            user_id=381268035,
            music_id_list=['834']
        )
        
        # 遍历结果
        for song_id, levels in dev_player_record.items():
            for level_index, record in levels.items():
                logger.info(
                    f'id:【{record.basic_info.id}】,'
                    f'title:【{record.basic_info.title}】,'
                    f'level:【{record.chart.level_lable}】,'
                    f'achievement:【{record.score_info.achievement}】'
                )
