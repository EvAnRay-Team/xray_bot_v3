from nonebot import logger, on_command
from nonebot.adapters import Message, Bot
from nonebot.params import CommandArg, Depends
from nonebot_plugin_orm import async_scoped_session
from src.dependencies.deps import get_user, get_adapter_name
from src.libraries.models import User
from src.libraries.schemas.mai import MaiMusic
from src.plugins.nonebot_plugin_maimai.lib.music_info import MaiMusicData
from src.libraries.tools.message_segment import MessageSegmentFactory
from ..deps import get_music_data

query_music_by_id = on_command("id", block=True)

@query_music_by_id.handle()
async def _(bot: Bot, session: async_scoped_session, music: MaiMusic = Depends(get_music_data), user: User = Depends(get_user), adapter_name: str = Depends(get_adapter_name)):
    music_data = await MaiMusicData(music.basic_info.id, False).draw()
    msg = MessageSegmentFactory.image(
        adapter_name=adapter_name,
        image=music_data,
        filename='music_data.png',
        format='PNG'
    )
    await query_music_by_id.finish(msg)
