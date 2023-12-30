# https://github.com/MathNodes/cosmospy-protobuf/blob/chain/sentinel/src/sentinel_protobuf/sentinel/types/v1/status.proto
from enum import Enum


class Status(Enum):
    UNSPECIFIED = 0
    ACTIVE = 1
    INACTIVE_PENDING = 2
    INACTIVE = 3

    def __str__(self):
        return f"Status{self.name.title()}"
