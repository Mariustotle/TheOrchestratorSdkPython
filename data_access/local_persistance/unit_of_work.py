from orchestrator_sdk.data_access.local_persistance.repositories.message_outbox_repository import MessageOutboxRepository
from orchestrator_sdk.data_access.local_persistance.repositories.message_history_repository import MessageHistoryRepository
from orchestrator_sdk.data_access.local_persistance.services.local_outbox_service import LocalOutboxService

from orchestrator_sdk.data_access.local_persistance.local_database import LocalDatabase
from sqlalchemy.orm import Session

from uuid import uuid4

import uuid
import asyncio

class UnitOfWork:    
    transaction_reference:uuid4 = None
    session:Session = None
    local_database:LocalDatabase = None
   
    # TODO: Create repository base class, making adding of repositories into a list not fixed set
    # TODO: Create two sessions, local_database and main_database but commit on the same time
    def __init__(self, local_database:LocalDatabase):
        
        self.local_database = local_database
        self.transaction_reference = uuid.uuid4()
        self.has_changes:bool = False        
        self.local_outbox_service = LocalOutboxService(local_database)

    def __enter__(self):
        self.session = self.local_database.db_session_maker()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        check_local_messages:bool = False
        
        if exc_type:
            self.session.rollback()
        else:            
            self.session.commit()
            if self._manual_commit():
                check_local_messages = True
            self.session.commit()        

        self.session.close()
        
        if check_local_messages:
            asyncio.create_task(self.local_outbox_service.check_for_messages_that_are_ready())
        
    def _manual_commit(self) -> bool:
        return self.message_outbox_repository.commit()

    @property
    def message_outbox_repository(self):
        return MessageOutboxRepository(self.session, self.transaction_reference)

    @property
    def message_history_repository(self):
        return MessageHistoryRepository()