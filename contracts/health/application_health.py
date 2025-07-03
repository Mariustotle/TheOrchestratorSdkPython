from pydantic import BaseModel
from typing import Optional, Dict
from orchestrator_sdk.contracts.health.health_status import HealthStatus
from orchestrator_sdk.contracts.health.outbox_summary import OutboxSummary

class ApplicationHealth(BaseModel):
    Status: HealthStatus
    HealthChecks: Dict[str, bool]
    OutboxSummary: OutboxSummary

    @staticmethod
    def Create(status: HealthStatus, health_checks: Dict[str, bool], outbox_summary: 'OutboxSummary') -> 'ApplicationHealth':

        return ApplicationHealth(
            Status = status,
            HealthChecks = health_checks,
            OutboxSummary = outbox_summary
        )
