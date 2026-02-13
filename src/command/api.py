from command.base import BaseCommand
from src.libraries.requests.mai import MaiRequestService
from src.server.mai_music_server import total_music
from nonebot.log import logger

import asyncio
import json

class Command(BaseCommand):
    def handle(self, **options):
        try:
            asyncio.run(self.get_music_info_payload(834))
        except KeyboardInterrupt:
            pass

    async def get_music_info_payload(self, music_id: int) -> dict:
        request_service = MaiRequestService()
        music = total_music.find_by_id(music_id)

        # 获取玩家记录（自动实体化为 MaiRecord）
        dev_player_record = await request_service.get_player_record(
            user_id=381268035,
            music_id_list=[music_id]
        )
        if music is None or music.charts is None or dev_player_record is None:
            print(f"未找到音乐 ID: {music_id}")
            return {}
        payload = {
            "basic_info": music.basic_info.model_dump(),
            "charts": music.charts.get_chart_list(dump=True),
            "records": [record.model_dump() for record in dev_player_record.records],
        }

        print(payload)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return payload
        
        # # 遍历结果
        # for record in dev_player_record:
        #     logger.info(
        #         f'id:【{record.basic_info.id}】,'
        #         f'title:【{record.basic_info.title}】,'
        #         f'level:【{record.chart.level_lable}】,'
        #         f'achievement:【{record.score_info.achievement}】'
        #     )
