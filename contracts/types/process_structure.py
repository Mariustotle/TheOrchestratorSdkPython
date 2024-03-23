
from enum import Enum

class ProcessStructure(Enum):
    Undefined = 0,
    Commands = 1,
    Events = 2,
    Batch = 3,
    Workflow = 4
