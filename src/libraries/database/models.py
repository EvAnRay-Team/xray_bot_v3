from datetime import datetime
from typing import Optional

from beanie import Document
from pymongo import IndexModel

from src.libraries.enums import AliasStatus


class Abstract(Document):
    music_id: int
    user_id: int
    nickname: str
    file_key: str
    create_time: datetime = datetime.now()
    update_time: datetime = datetime.now()

    class Settings:
        indexes = [
            IndexModel("music_id"),
            IndexModel("user_id"),
        ]


class Alias(Document):
    music_id: int
    alias: str
    title: str
    status: int  # 别名状态
    create_time: datetime = datetime.now()
    update_time: datetime = datetime.now()

    class Settings:
        indexes = [
            IndexModel("music_id"),
            IndexModel("alias"),
        ]


class AliasApply(Document):
    id: int  # 投票ID
    music_id: int
    alias: str
    user_id: int
    group_id: int
    status: AliasStatus
    create_time: datetime = datetime.now()
    update_time: datetime = datetime.now()

    class Settings:
        indexes = [
            IndexModel("id", unique=True),
            IndexModel("music_id"),
            IndexModel("user_id"),
        ]


class AliasVote(Document):
    id: int  # 投票ID
    user_id: int
    group_id: int
    score: int  # +1/-1
    create_time: datetime = datetime.now()

    class Settings:
        indexes = [
            IndexModel("id"),
            IndexModel("user_id"),
        ]


class UserConfig(Document):
    user_id: int
    is_abstract: bool
    maimai_best_50_style: str
    maimai_icon: Optional[str] = None
    maimai_plate: Optional[str] = None
    maimai_frame: Optional[str] = None
    chu_prober_mode: str
    create_group: Optional[int] = None
    create_time: datetime = datetime.now()

    class Settings:
        indexes = [
            IndexModel("user_id", unique=True),
        ]
