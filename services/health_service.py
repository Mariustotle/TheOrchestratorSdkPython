from typing import Dict
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from orchestrator_sdk.data_access.database.repositories.message_outbox_repository import MessageOutboxRepository
from orchestrator_sdk.contracts.health.health_status import HealthStatus
from orchestrator_sdk.contracts.health.application_health import ApplicationHealth
from orchestrator_sdk.data_access.database.unit_of_work import UnitOfWork
from uuid import uuid4
from orchestrator_sdk.seedworks.logger import Logger

import asyncio

logger = Logger.get_instance()

class HealthService:

    _uow: UnitOfWork

    def __init__(self, uow:UnitOfWork):
        self._uow = uow    
            
    async def do_health_check(self) -> 'ApplicationHealth':
        
        status = HealthStatus.Healthy
        health_checks:Dict[str, bool] = dict()

        try:

            repo = self._uow.get_repository(MessageOutboxRepository)
            outbox_summary = await repo.get_outbox_summary_async()
            health_checks['Outbox database access checked'] = True            
            
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Failed to do health checks. Details: {ex}")
            status = HealthStatus.Failed

        return ApplicationHealth.Create(status=status, health_checks=health_checks, outbox_summary=outbox_summary)
        

        

        




        
        
        
 
    
    