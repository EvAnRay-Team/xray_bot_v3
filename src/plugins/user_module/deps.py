from collections.abc import Awaitable, Callable

from nonebot.adapters import Bot, Event
from nonebot.params import Depends
from nonebot_plugin_orm import get_scoped_session

from src.plugins.user_module.models.config_base import ConfigBase
from src.plugins.user_module.models.user import User

from .crud import create_user, get_user_by_adapter_and_external_id
from .crud import create_user_config as crud_create_user_config
from .crud import get_user_config as crud_get_user_config


async def get_user(bot: Bot, event: Event) -> User:
    """
    依赖注入专用：自动获取并返回当前指令触发用户对象，不建议手动调用。
    若用户不存在则自动创建。
    """
    adapter_name = bot.adapter.get_name()

    session = get_scoped_session()
    user_id = event.get_user_id()
    user = await get_user_by_adapter_and_external_id(session, adapter_name, user_id)
    if user is None:
        user = await create_user(session, adapter_name, user_id)
    return user


def get_user_config(
    config_cls: type[ConfigBase],
) -> Callable[..., Awaitable[ConfigBase]]:
    """
    通用用户配置依赖注入工厂，自动获取当前用户的指定配置。
    用法：Depends(get_user_config(TestModuleConfig))
    """

    async def dependency(
        user: User = Depends(get_user),
    ):
        session = get_scoped_session()
        config = await crud_get_user_config(session, config_cls, user.id)
        if config is None:
            config = await crud_create_user_config(session, config_cls, user.id)
        return config

    return dependency
