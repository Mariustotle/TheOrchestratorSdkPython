
from enum import Enum

class HealthStatus(Enum):
    Undefined = 0,
    Healthy = 1,
    RequiresIntervention = 2,
    Failed = 3