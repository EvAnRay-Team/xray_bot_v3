from nonebot import on_command
from nonebot.params import Depends
from nonebot_plugin_orm import async_scoped_session

from src.plugins.test_module.config import TestModuleConfig
from src.plugins.user_module.deps import get_user_config

PingCommand = on_command("ping", block=True)


@PingCommand.handle()
async def _(config: TestModuleConfig = Depends(get_user_config(TestModuleConfig))):
    if config.reply_uuid:
        await PingCommand.send(f"Hello, user ID: {config.user_id}")
    await PingCommand.finish("Pong!")


ReplyUUIDCommand = on_command("reply_uuid", block=True)


@ReplyUUIDCommand.handle()
async def _(
    session: async_scoped_session,
    config: TestModuleConfig = Depends(get_user_config(TestModuleConfig)),
):
    config.reply_uuid = not config.reply_uuid
    status = "enabled" if config.reply_uuid else "disabled"
    await session.commit()
    await ReplyUUIDCommand.finish(f"Reply UUID has been {status}.")
