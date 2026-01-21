from enum import IntEnum


class AliasStatus(IntEnum):
    SCORING = 0
    TIMEOUT = 1
    PASSED = 2
    ADMIN_PASSED = 3
    ADMIN_REJECTED = 4
