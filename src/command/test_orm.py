from command.base import BaseCommand
import asyncio
from plugins.user_module.models.test_orm import TestOrm
from nonebot_plugin_orm import get_session

class Command(BaseCommand):
    def handle(self, **options):
        asyncio.run(self.run_async())

    async def run_async(self):
        async with get_session() as session:
            test_orm = TestOrm(name="test", value=1)
            session.add(test_orm)
            await session.commit()
            await session.refresh(test_orm)
            print(test_orm)