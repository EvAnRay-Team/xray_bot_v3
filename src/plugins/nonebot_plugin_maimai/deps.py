from nonebot.adapters import Message
from nonebot.params import CommandArg, Depends
from nonebot.internal.matcher import Matcher  # 导入 Matcher 类型
from src.libraries.schemas.mai import MaiMusic
from src.server.mai_music_server import total_music


async def get_music_data(matcher: Matcher, args: Message = CommandArg()) -> MaiMusic:
    """
    根据用户给出的参数查询歌曲，如果找到歌曲则返回歌曲信息，否则结束当前事件处理

    :param args: 命令参数
    :return: 歌曲信息
    """
    arg = args.extract_plain_text().strip()

    # 尝试通过歌曲ID
    if arg.isdigit():
        music = total_music.find_by_id(int(arg))
        if music:
            return music
        
    # 尝试通过歌曲别名


    # 尝试通过歌曲标题
    await matcher.finish(
        "请提供有效的歌曲关键词，如歌曲ID、别名、曲名。"
    )
