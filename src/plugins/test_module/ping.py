from nonebot import on_command
from nonebot.params import Depends

from src.plugins.test_module.config import TestModuleConfig
from src.plugins.user_module.deps import get_user_config

PingCommand = on_command("ping", block=True)

@PingCommand.handle()
async def _(config: TestModuleConfig = Depends(get_user_config(TestModuleConfig))):
    await PingCommand.send(f"Hello, user ID: {config.user_id}")
    await PingCommand.finish("Pong!")
