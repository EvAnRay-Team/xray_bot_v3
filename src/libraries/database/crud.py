from typing import Optional

from nonebot_plugin_orm import AsyncSession
from sqlalchemy import select

from src.libraries.enums import PlatfromType

from .models import User


async def get_user_by_platform_id(
    session: AsyncSession, platform: PlatfromType, user_id: str | int
) -> Optional[User]:
    stmt = select(User)

    if platform == PlatfromType.ONEBOT_V11:
        stmt = stmt.where(User.qid == int(user_id))

    elif platform == PlatfromType.QQ_DIRECT:
        stmt = stmt.where(User.user_openid == str(user_id))
    elif platform == PlatfromType.QQ_GROUP:
        stmt = stmt.where(User.group_openid == str(user_id))
    elif platform == PlatfromType.QQ_GUILD:
        stmt = stmt.where(User.member_user_id == str(user_id))

    result = await session.execute(stmt)

    return result.scalar_one_or_none()

async def create_user(
        session: AsyncSession,
        platform: PlatfromType,
        user_id: str | int
) -> User:
    new_user = User()

    if platform == PlatfromType.ONEBOT_V11:
        new_user.qid = int(user_id)

    elif platform == PlatfromType.QQ_DIRECT:
        new_user.user_openid = str(user_id)
    elif platform == PlatfromType.QQ_GROUP:
        new_user.group_openid = str(user_id)
    elif platform == PlatfromType.QQ_GUILD:
        new_user.member_user_id = str(user_id)

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user
