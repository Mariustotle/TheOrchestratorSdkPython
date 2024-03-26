from enum import Enum

class OutboxStatus(Enum):
    Undefined = 0
    Pending = 1
    Ready = 2
    Retry = 3
    Failed = 4
    Published = 5
    Preperation = 6
    Rollback = 7
    Duplicate = 8
