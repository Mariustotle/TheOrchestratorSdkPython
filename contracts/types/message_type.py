
from enum import Enum

class MessageType(Enum):
    Undefined = 0
    Command = 1
    Event = 2
    OutboundStreamEvent = 3
    OutboundStream = 4