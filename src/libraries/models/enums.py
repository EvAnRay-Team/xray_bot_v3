from enum import IntEnum
from enum import Enum

class AliasStatus(IntEnum):
    SCORING = 0
    TIMEOUT = 1
    PASSED = 2
    ADMIN_PASSED = 3
    ADMIN_REJECTED = 4

class BindType(str, Enum):
    REQUEST = "request"
    CONFIRM = "confirm"
