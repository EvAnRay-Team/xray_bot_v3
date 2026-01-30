import datetime

from nonebot import on_command
from nonebot.params import Depends
from nonebot.adapters.discord import Bot, MessageEvent, MessageSegment, Message, GuildMessageCreateEvent
from src.dependencies.deps import get_user
from src.libraries.models.user import User
from nonebot.adapters.discord import api as discord_api

matcher = on_command('send')

@matcher.handle()
async def ready(bot: Bot, event: GuildMessageCreateEvent):
    await matcher.finish(Message(
            [
                MessageSegment.mention_user(event.user_id),
                MessageSegment.timestamp(datetime.datetime.now(),style=discord_api.TimeStampStyle.RelativeTime)
                # MessageSegment.text(f"你的ID是:{user.id},创建时间为：「{user.create_time}」")
            ]
        )
    )
