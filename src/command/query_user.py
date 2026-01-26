from command.base import BaseCommand
import asyncio
from sqlalchemy import select
from plugins.user_module.models.user import User
from nonebot_plugin_orm import get_session

class Command(BaseCommand):
    def handle(self, **options):
        # 注意：由于 run.py 里可能已经有了事件循环，或者需要新建
        # 推荐使用 asyncio.run
        asyncio.run(self.run_async())

    async def run_async(self):
        # 直接使用 get_session 获取异步连接
        async with get_session() as session:
            # 构造查询
            stmt = select(User)
            result = await session.execute(stmt)
            users = result.scalars().all()
            
            if not users:
                print("未找到任何用户记录。")
                return

            for user in users:
                # 根据你的 User 模型字段打印
                print(f"ID: {user.id} | Create_time : {getattr(user, 'create_time', 'N/A')}")