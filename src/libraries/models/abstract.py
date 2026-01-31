from datetime import datetime

from nonebot_plugin_orm import Model
from sqlalchemy.orm import Mapped, mapped_column

class Abstract(Model):
    __tablename__ = "abstracts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    music_id: Mapped[int]
    user_id: Mapped[str]
    nickname: Mapped[str]
    file_key: Mapped[str]
    create_time: Mapped[datetime] = mapped_column(default=datetime.now)
    update_time: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

    def __str__(self) -> str:
        return f"id: {self.id}, music_id: {self.music_id}, user_id: {self.user_id}, nickname: {self.nickname}, file_key: {self.file_key}, create_time: {self.create_time}, update_time: {self.update_time}"
