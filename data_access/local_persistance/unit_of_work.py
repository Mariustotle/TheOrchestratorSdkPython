

from orchestrator_sdk.data_access.local_persistance.repositories.message_outbox_repository import MessageOutboxRepository
from uuid import uuid4
import uuid

class UnitOfWork:
    
    transaction_reference:uuid4 = None
    
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session = None
        self.has_changes = False
        
        # Add this transaction reference to an application context that can be referenced without using parameters
        self.transaction_reference = uuid.uuid4()       

    def __enter__(self):
        self.session = self.session_factory()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
        else:            
            self.session.commit()
            self._manual_commit()
            self.session.commit()
        self.session.close()        
        
    def _manual_commit(self):
        self.message_outbox_repository.commit()

    @property
    def message_outbox_repository(self):
        return MessageOutboxRepository(self.session, self.transaction_reference)
