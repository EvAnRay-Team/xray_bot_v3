from datetime import datetime
from uuid import UUID

from nonebot_plugin_orm import Model
from sqlalchemy import ForeignKey

try:
    from sqlalchemy.dialects.postgresql import JSONB

    JSONType = JSONB
except ImportError:
    from sqlalchemy import JSON

    JSONType = JSON
from sqlalchemy.orm import Mapped, mapped_column


class User(Model):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    create_time: Mapped[datetime] = mapped_column(default=datetime.now)


class UserAuth(Model):
    __tablename__ = "user_auths"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    external_id: Mapped[str] = mapped_column(unique=True, nullable=True)
    type: Mapped[str]  # 认证类型，如 'qq', 'wechat' 等
    ext: Mapped[dict] = mapped_column(JSONType, default=dict, nullable=True)
