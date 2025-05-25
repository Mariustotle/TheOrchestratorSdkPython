
from enum import Enum

class ProcessStructure(Enum):
    Undefined = 0,
    Commands = 1,
    Events = 2,
    EventStream = 3,
    EventSnapshot = 4,
    Batch = 5,
    Workflow = 6
