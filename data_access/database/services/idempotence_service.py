from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from orchestrator_sdk.data_access.database.repositories.message_history_repository import MessageHistoryRepository
from orchestrator_sdk.data_access.database.unit_of_work import UnitOfWork
from uuid import uuid4

import asyncio

class IdempotenceService:
    
    last_timestamp:datetime = None
    min_cleanup_interval_in_hours:int = 5
    retention_period_in_days:int = 30

    async def has_message_been_processed(self, message_id:uuid4, unit_of_work:UnitOfWork) -> bool:
        now = datetime.utcnow()
        do_cleanup:bool = True if self.last_timestamp is None or now - self.last_timestamp > timedelta(hours=1) else False
        
        has_been_processed = await unit_of_work.message_history_repository.has_message_been_processed(message_id=message_id)
        
        
        if do_cleanup:
            asyncio.create_task(self.cleanup(unit_of_work.message_database.db_session_maker()))
            
        return has_been_processed
            
    async def cleanup(self, independant_session: Session):
        history_repo = MessageHistoryRepository(independant_session)
        self.last_timestamp = datetime.utcnow()        
        
        await history_repo.delete_old_message_history(retention_in_days=self.retention_period_in_days)
        
        independant_session.commit()
        independant_session.close()
    
    