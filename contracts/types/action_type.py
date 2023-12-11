
from enum import Enum

class ActionType(Enum):
    Undefined = 0,
    Process = 1,
    OnSuccess = 2,
    Callback = 3,
    Transition = 4,
    Interaction = 5