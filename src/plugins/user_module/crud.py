from uuid import UUID, uuid4
from nonebot_plugin_orm import AsyncSession
from sqlalchemy import select

from .models import User


def get_user_adapter_field(adapter: str, adapter_id: str | int) -> tuple:
    match adapter:
        case "OneBot V11":
            return User.qid, int(adapter_id)
        case "QQ":
            return User.openid, str(adapter_id)
        case _:
            error_message = "Unsupported adapter: {}"
            raise ValueError(error_message.format(adapter))



async def get_user_by_id(
    session: AsyncSession, adapter: str, adapter_id: str | int
) -> User | None:
    field, value = get_user_adapter_field(adapter, adapter_id)
    stmt = select(User).where(field == value)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession, adapter: str, adapter_id: str | int
) -> User:
    new_user = User()
    new_user.id = uuid4()
    field, value = get_user_adapter_field(adapter, adapter_id)
    setattr(new_user, field.key, value)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user
