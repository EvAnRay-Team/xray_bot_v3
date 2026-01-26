from datetime import datetime

from nonebot_plugin_orm import Model
from sqlalchemy.orm import Mapped, mapped_column



class Abstract(Model):
    __tablename__ = "abstracts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    music_id: Mapped[int]
    user_id: Mapped[int]
    nickname: Mapped[str]
    file_key: Mapped[str]
    create_time: Mapped[datetime] = mapped_column(default=datetime.now)
    update_time: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )
