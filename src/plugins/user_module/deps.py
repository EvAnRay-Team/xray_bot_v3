from nonebot.adapters import Bot, Event
from nonebot_plugin_orm import async_scoped_session

from src.plugins.user_module.models import User

from .crud import create_user, get_user_by_id


async def get_user(bot: Bot, event: Event, session: async_scoped_session) -> User:
    adapter_name = bot.adapter.get_name()

    async_session = session.session_factory()
    user_id = event.get_user_id()
    user = await get_user_by_id(async_session, adapter_name, user_id)

    if user is None:
        user = await create_user(async_session, adapter_name, user_id)

    return user
