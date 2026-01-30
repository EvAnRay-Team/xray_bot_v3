from nonebot import logger, on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg, Depends
from nonebot_plugin_orm import async_scoped_session
from src.dependencies.deps import get_user
from src.libraries.models.user import User
from src.libraries.schemas.mai import MaiMusic
from ..deps import get_music_data

QueryMusicByID = on_command("id", block=True)

@QueryMusicByID.handle()
async def _(session: async_scoped_session, music: MaiMusic = Depends(get_music_data), user: User = Depends(get_user)):
    await QueryMusicByID.finish(f"找到歌曲：{music.basic_info.title}")