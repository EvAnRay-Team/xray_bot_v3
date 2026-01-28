from datetime import UTC, datetime, timedelta

from nonebot.params import Depends
from nonebot.rule import to_me
from nonebot_plugin_orm import get_scoped_session
from sqlalchemy import select

from src.libraries.models.bind import BindToken
from src.dependencies.deps import get_user
from src.libraries.models.user import User


# 这是一个用于限制命令触发频率的守卫逻辑，防止用户在短时间内生成过多的 BindToken。
async def check_token_usage(session, user: User) -> bool:
    
    # 修改方案 A：直接获取不带时区的本地时间（推荐，除非你的服务器跨时区部署）
    now = datetime.now()
    
    # 修改方案 B：如果你想坚持用 UTC，但要去掉时区标记以匹配数据库
    # now = datetime.now(UTC).replace(tzinfo=None)
    
    day_ago = now - timedelta(hours=24)
    
    tokens = await session.scalars(
        select(BindToken)
        .where(BindToken.main_user_id == user.id)
        .where(BindToken.created_at >= day_ago) # 现在 day_ago 也是 Naive 了
    )
    # 性能小提示：如果只是为了计数，用 .count() 比 list(tokens) 更 Pythonic 且高效
    token_list = tokens.all()
    return len(token_list) <= 8
