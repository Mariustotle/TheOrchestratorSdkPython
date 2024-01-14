from orchestrator_sdk.data_access.local_persistance.repositories.message_outbox_repository import MessageOutboxRepository
from orchestrator_sdk.data_access.local_persistance.repositories.message_history_repository import MessageHistoryRepository
from orchestrator_sdk.data_access.local_persistance.services.local_outbox_service import LocalOutboxService

from orchestrator_sdk.data_access.local_persistance.database_context import DatabaseContext
from typing import Optional
from sqlalchemy.orm import Session

from uuid import uuid4

import uuid
import asyncio

class UnitOfWork:    
    transaction_reference:uuid4 = None
    has_application_session:bool = False
    has_changes:bool = False
    
    message_database:DatabaseContext = None
    message_session:Session = None
    
    application_database:Optional[DatabaseContext] = None
    application_session:Optional[Session] = None
   
    # TODO: Create repository base class, making adding of repositories into a list not fixed set
    def __init__(self, message_database:DatabaseContext, application_database:DatabaseContext = None):
        
        self.message_database = message_database
        
        if (application_database != None):
            self.has_application_session = True        
            self.application_database = application_database
            
        self.transaction_reference = uuid.uuid4()
        self.local_outbox_service = LocalOutboxService(message_database)


    def __enter__(self):
        self.message_session = self.message_database.db_session_maker()
        
        if (self.application_database != None) :
            self.application_session = self.application_database.db_session_maker()
        
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        
        if exc_type:
            self.message_session.rollback()
            
            if (self.has_application_session):
                self.application_session.rollback()
                
        else:
            self.message_session.commit()
            self._preparing_outbox_messages()
            
            if (self.has_application_session):
                self.application_session.commit()            
            
            self._committing_outbox_messages()
            
            if (self.has_changes):
                self._run_post_commit_processes()

        self.message_session.close()        
    
    def _preparing_outbox_messages(self):
        self.has_changes = self.message_outbox_repository.prepare_outbox_message_for_transaction()
        
        if (self.has_changes):
            self.message_session.commit()
    
    def _committing_outbox_messages(self):
        self.has_changes = self.message_outbox_repository.complete_outbox_message_in_transaction()
        
        if (self.has_changes):
            self.message_session.commit()
    
    def _run_post_commit_processes(self):
        if (self.has_changes):
            asyncio.create_task(self.local_outbox_service.check_for_messages_that_are_ready())  
    

    @property
    def message_outbox_repository(self):
        return MessageOutboxRepository(self.message_session, self.transaction_reference)

    @property
    def message_history_repository(self):
        return MessageHistoryRepository()