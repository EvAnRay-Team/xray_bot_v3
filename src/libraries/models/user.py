from datetime import datetime
from uuid import UUID

import nonebot
from nonebot_plugin_orm import Model
from sqlalchemy import ForeignKey, JSON

try:
    from sqlalchemy.dialects.postgresql import JSONB
except ImportError:
    JSONB = None

try:
    driver = nonebot.get_driver()
    # Check if utilizing PostgreSQL
    db_url = str(getattr(driver.config, "sqlalchemy_database_url", ""))
    print(db_url)
    if "postgres" in db_url and JSONB:
        JSONType = JSONB
    else:
        JSONType = JSON
except Exception:
    # Fallback if driver not initialized or config missing
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
