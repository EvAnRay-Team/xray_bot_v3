from datetime import datetime
from uuid import UUID

from nonebot_plugin_orm import Model
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from plugins.user_module.enums import BindType


class BindToken(Model):
    __tablename__ = "bind_tokens"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(unique=True, nullable=False)
    main_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    type: Mapped[BindType] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    sub_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
