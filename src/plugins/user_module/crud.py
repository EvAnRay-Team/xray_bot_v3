from uuid import UUID, uuid4

from nonebot_plugin_orm import async_scoped_session
from sqlalchemy import select

from src.libraries.models import ConfigBase, User, UserAuth

from src.libraries.models.enums import AdapterType
from .exceptions import UnsupportedAdapterError


def get_adapter_type_by_name(adapter: str) -> AdapterType:
    match adapter:
        case "OneBot V11":
            return AdapterType.ONEBOT_V11
        case "QQ":
            return AdapterType.QQ
        case _:
            raise UnsupportedAdapterError(adapter)


def get_user_auth_type_and_external_id(
    adapter: str, external_id: str | int
) -> tuple[AdapterType, str]:
    adapter_type = get_adapter_type_by_name(adapter)
    return adapter_type, str(external_id)


async def get_user_by_adapter_and_external_id(
    session: async_scoped_session, adapter: str, external_id: str | int
) -> User | None:
    auth_type, normalized_external_id = get_user_auth_type_and_external_id(
        adapter, external_id
    )
    stmt = (
        select(User)
        .join(UserAuth, User.id == UserAuth.user_id)
        .where(
            UserAuth.type == auth_type.value,
            UserAuth.external_id == normalized_external_id,
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(
    session: async_scoped_session, adapter: str, adapter_id: str | int
) -> User:
    new_user = User()
    new_user.id = uuid4()
    session.add(new_user)
    await session.flush()  # 先写入user，获取id
    auth_type, external_id = get_user_auth_type_and_external_id(adapter, adapter_id)
    new_auth = UserAuth(
        id=uuid4(), user_id=new_user.id, external_id=external_id, type=auth_type.value
    )
    session.add(new_auth)
    await session.flush()
    await session.refresh(new_user)
    return new_user


async def get_user_config(
    session: async_scoped_session, config_cls: type[ConfigBase], user_id: UUID
) -> ConfigBase | None:
    stmt = select(config_cls).where(config_cls.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user_config(
    session: async_scoped_session, config_cls: type[ConfigBase], user_id: UUID
) -> ConfigBase:
    config = config_cls(user_id=user_id, id=uuid4())
    session.add(config)
    await session.flush()
    await session.refresh(config)
    return config
