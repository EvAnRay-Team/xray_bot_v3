from command.base import BaseCommand
from libraries.providers.mai import DivingFishMaiApi
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
        # music_data = await DivingFishMaiApi().music_data()
        # print(music_data)
        dev_player_record = await DivingFishMaiApi().dev_player_record(user_id=381268035,music_id_list=['834'])
        for _, levels in dev_player_record.items():
            for _, record in levels.items():
                logger.info(f'id:【{record.basic_info.id}】,title:【{record.basic_info.title}】,level:【{record.chart.level_lable}】,achievement:【{record.score_info.achievement}】')
                # print(record.score_info.achievement)
