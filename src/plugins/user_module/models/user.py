from nonebot_plugin_orm import Model
from sqlalchemy.orm import Mapped, mapped_column


class User(Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    qid: Mapped[int | None] = mapped_column(unique=True, nullable=True)
    group_openid: Mapped[str | None] = mapped_column(unique=True, nullable=True)
    user_openid: Mapped[str | None] = mapped_column(unique=True, nullable=True)
    member_user_id: Mapped[str | None] = mapped_column(unique=True, nullable=True)
