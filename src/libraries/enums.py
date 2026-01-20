from enum import Enum, IntEnum


class PlatfromType(Enum):
    ONEBOT_V11 = "onebot_v11"
    QQ_DIRECT = "qq_direct"
    QQ_GROUP = "qq_group"
    QQ_GUILD = "qq_guild"


class AliasStatus(IntEnum):
    SCORING = 0
    TIMEOUT = 1
    PASSED = 2
    ADMIN_PASSED = 3
    ADMIN_REJECTED = 4
