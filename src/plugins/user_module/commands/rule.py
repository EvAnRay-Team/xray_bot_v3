from datetime import UTC, datetime, timedelta

from nonebot.params import Depends
from nonebot.rule import to_me
from nonebot_plugin_orm import get_scoped_session
from sqlalchemy import select

from src.libraries.models.bind import BindToken
from src.plugins.user_module.deps import get_user
from src.libraries.models.user import User



async def request_token_rule(user: User = Depends(get_user)) -> bool:
    session = get_scoped_session()
    now = datetime.now(UTC)
    day_ago = now - timedelta(hours=24)
    tokens = await session.scalars(
        select(BindToken)
        .where(BindToken.main_user_id == user.id)
        .where(BindToken.created_at >= day_ago)
    )
    token_list = list(tokens)
    return not len(token_list) > 8

request_rule = to_me() & request_token_rule
