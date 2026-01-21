from nonebot import on_command
from nonebot.params import Depends

from src.plugins.user_module.deps import get_user
from src.plugins.user_module.models.user import User

PingCommand = on_command("ping", block=True)

@PingCommand.handle()
async def _(user: User = Depends(get_user)):
    await PingCommand.send(f"Hello, user ID: {user.id}")
    await PingCommand.finish("Pong!")
