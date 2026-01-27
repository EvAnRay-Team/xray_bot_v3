from sqlalchemy.orm import Mapped, mapped_column

from src.libraries.models.config_base import ConfigBase


class TestModuleConfig(ConfigBase):
    """测试模块配置类"""
    __tablename__ = "user_test_configs"
    reply_uuid: Mapped[bool] = mapped_column(default=False)
