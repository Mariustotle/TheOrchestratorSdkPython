
from enum import Enum

class PublishAdapter(Enum):
    Undefined = 0,
    Queue = 1
    Concurrent = 2
