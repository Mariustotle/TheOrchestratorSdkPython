
from enum import Enum

class PublishAdapter(Enum):
    Undefined = 0,
    Local = 1
    Direct = 2
    Outbox = 3
