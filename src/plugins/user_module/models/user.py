from uuid import UUID

from nonebot_plugin_orm import Model
from sqlalchemy import BIGINT
from sqlalchemy.orm import Mapped, mapped_column


class User(Model):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    qid: Mapped[int | None] = mapped_column(BIGINT, unique=True, nullable=True)
    openid: Mapped[str | None] = mapped_column(unique=True, nullable=True)
    create_time: Mapped[str] = mapped_column(default="")
