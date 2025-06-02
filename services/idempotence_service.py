from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from orchestrator_sdk.data_access.database.repositories.message_history_repository import MessageHistoryRepository
from orchestrator_sdk.data_access.database.unit_of_work import UnitOfWork
from uuid import uuid4
from sdk.logging.logger import Logger

import asyncio

logger = Logger.get_instance()

class IdempotenceService:
    
    last_timestamp:datetime = None
    min_cleanup_interval_in_hours:int = 2
    retention_period_in_days:int = 3

    async def has_message_been_processed(self, message_id:uuid4, unit_of_work:UnitOfWork) -> bool:
        do_cleanup:bool = True if self.last_timestamp is None or (datetime.utcnow() - self.last_timestamp) > timedelta(hours=self.min_cleanup_interval_in_hours) else False
        
        has_been_processed = await unit_of_work.message_history_repository.has_message_been_processed(message_id=message_id)       
        
        if do_cleanup:
            asyncio.create_task(self.cleanup(unit_of_work.message_database.db_session_maker()))
            
        return has_been_processed
            
    async def cleanup(self, independant_session: Session):
        try:       
            history_repo = MessageHistoryRepository(independant_session)           
                    
            await history_repo.delete_old_message_history(retention_in_days=self.retention_period_in_days)

            independant_session.commit()
            independant_session.close()
            self.last_timestamp = datetime.utcnow()        
        
        except Exception as ex: 
            logger.error(f'Failed to perform idempotence local db cleanup. Details: {ex}')
            raise
        
        
        
        
 
    
    