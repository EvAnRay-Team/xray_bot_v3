from enum import Enum


class AdapterType(str, Enum):
    ONEBOT_V11 = "OneBot V11"
    QQ = "qq"
from enum import IntEnum


class AliasStatus(IntEnum):
    SCORING = 0
    TIMEOUT = 1
    PASSED = 2
    ADMIN_PASSED = 3
    ADMIN_REJECTED = 4

class BindType(str, Enum):
    REQUEST = "request"
    CONFIRM = "confirm"
