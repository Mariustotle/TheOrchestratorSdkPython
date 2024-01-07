from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from orchestrator_sdk.data_access.local_persistance.repositories.message_history_repository import MessageHistoryRepository

from uuid import uuid4

from orchestrator_sdk.data_access.local_persistance.unit_of_work import UnitOfWork

class IdempotenceService:
    
    last_timestamp:datetime = None
    min_cleanup_interval_in_hours:int = 5
    retention_period_in_days:int = 30

    async def has_message_been_processed(self, message_id:uuid4, unit_of_work:UnitOfWork) -> bool:
        now = datetime.utcnow()
        do_cleanup:bool = True if self.last_timestamp is None or now - self.last_timestamp > timedelta(hours=1) else False
        
        has_been_processed = await unit_of_work.message_history_repository.has_message_been_processed(message_id=message_id)
        self.last_timestamp = now
        if do_cleanup:
            # test with await then remove it
            await self.cleanup(unit_of_work.session_factory())
            
        return has_been_processed
            
    # Want this to clean up outside of the transaction scope of the incomming request
    async def cleanup(self, session:Session):
        history_repo = MessageHistoryRepository(session)
        history_repo.delete_old_message_history(retention_in_days=self.retention_period_in_days)
        session.commit()
        
    
    