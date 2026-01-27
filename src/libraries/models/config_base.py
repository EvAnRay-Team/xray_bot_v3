from uuid import UUID

from nonebot_plugin_orm import Model
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class ConfigBase(Model):
    """
    用户配置基类，所有用户配置类都应继承此类。
    """
    __abstract__ = True
    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
