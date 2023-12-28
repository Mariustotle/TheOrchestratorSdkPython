
from enum import Enum

class ActionType(Enum):
    Undefined = 0,
    Process = 1,
    Rollback = 2,
    Transition = 3,
    Interact = 4,    
    OnSuccess = 99
    
    