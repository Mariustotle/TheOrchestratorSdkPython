
from enum import Enum

class ProcessStructure(Enum):
    Undefined = 0,
    ConcurrentCommands = 1,
    QueueCommands = 2,
    ConcurrentEvents = 3,
    QueueEvents = 4,
    Batch = 5,
    Workflow = 6
