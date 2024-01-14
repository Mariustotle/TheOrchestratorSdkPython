from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from orchestrator_sdk.data_access.local_persistance.repositories.message_history_repository import MessageHistoryRepository
from orchestrator_sdk.data_access.local_persistance.message_database import MessageDatabase
from uuid import uuid4

import asyncio

class IdempotenceService:
    
    last_timestamp:datetime = None
    min_cleanup_interval_in_hours:int = 5
    retention_period_in_days:int = 30    
    message_history_repo:MessageHistoryRepository = None
    
    def __init__(self) -> None:
        self.message_history_repo = MessageHistoryRepository()

    async def has_message_been_processed(self, message_id:uuid4, session:Session, message_database:MessageDatabase) -> bool:
        now = datetime.utcnow()
        do_cleanup:bool = True if self.last_timestamp is None or now - self.last_timestamp > timedelta(hours=1) else False
        
        has_been_processed = await self.message_history_repo.has_message_been_processed(message_id=message_id, session=session)
        
        
        if do_cleanup:
            asyncio.create_task(self.cleanup(message_database))
            
        return has_been_processed
            
    async def cleanup(self, message_database:MessageDatabase):        
        session = message_database.db_session_maker()
        self.last_timestamp = datetime.utcnow()
        
        history_repo = MessageHistoryRepository()
        await history_repo.delete_old_message_history(retention_in_days=self.retention_period_in_days, session=session)
        
        session.commit()
        session.close()
    
    