from enum import Enum

class OutboxStatus(Enum):
    Undefined = 0
    Pending = 1
    Ready = 2
    Retry = 3
    Failed = 4
