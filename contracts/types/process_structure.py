
from enum import Enum

class ProcessStructure(Enum):
    Undefined = 0,
    Commands = 1,
    Events = 2,
    StreamInbound = 3,
    StreamOutbound = 4,
    Snapshot = 5,
    Batch = 6,
    Workflow = 7
