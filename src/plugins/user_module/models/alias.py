
from datetime import datetime

from nonebot_plugin_orm import Model
from sqlalchemy.orm import Mapped, mapped_column

from src.plugins.user_module.enums import AliasStatus


class Abstract(Model):
    __tablename__ = "abstracts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    music_id: Mapped[int]
    user_id: Mapped[int]
    nickname: Mapped[str]
    file_key: Mapped[str]
    create_time: Mapped[datetime] = mapped_column(default=datetime.now)
    update_time: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

class Alias(Model):
    __tablename__ = "aliases"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    music_id: Mapped[int]
    alias: Mapped[str]
    title: Mapped[str]
    status: Mapped[int]
    create_time: Mapped[datetime] = mapped_column(default=datetime.now)
    update_time: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

class AliasApply(Model):
    __tablename__ = "alias_applies"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    music_id: Mapped[int]
    alias: Mapped[str]
    user_id: Mapped[int]
    group_id: Mapped[int]
    status: Mapped[AliasStatus]
    create_time: Mapped[datetime] = mapped_column(default=datetime.now)
    update_time: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

class AliasVote(Model):
    __tablename__ = "alias_votes"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int]
    group_id: Mapped[int]
    score: Mapped[int]
    create_time: Mapped[datetime] = mapped_column(default=datetime.now)

class UserConfig(Model):
    __tablename__ = "user_configs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int]
    is_abstract: Mapped[bool]
    maimai_best_50_style: Mapped[str]
    maimai_icon: Mapped[str | None]
    maimai_plate: Mapped[str | None]
    maimai_frame: Mapped[str | None]
    chu_prober_mode: Mapped[str]
    create_group: Mapped[int | None]
    create_time: Mapped[datetime] = mapped_column(default=datetime.now)
