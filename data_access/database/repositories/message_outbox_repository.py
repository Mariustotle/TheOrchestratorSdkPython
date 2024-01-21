from orchestrator_sdk.data_access.database.entities.message_outbox_entity import MessageOutboxEntity
from orchestrator_sdk.contracts.local_persistence.message_outbox_schema import MessageOutboxSchema
from orchestrator_sdk.data_access.database.outbox_status import OutboxStatus
from orchestrator_sdk.data_access.database.repository_base import RepositoryBase

from sqlalchemy.orm import Session
from uuid import uuid4
from typing import List

from datetime import datetime, timedelta


class ReadyForSubmissionBatch:
    messages_ready:int = None
    messages_not_completed:int = None
    messages_needing_intervention:int = None
    messages:List[MessageOutboxEntity] = None
    
    def Create(self, 
        messages_ready:int,
        messages_not_completed:int,
        message_needing_intervention:int,
        messages:[MessageOutboxEntity] = None):
        
        self.messages_ready = messages_ready
        self.messages_needing_intervention = message_needing_intervention
        self.messages_not_completed = messages_not_completed
        self.messages = messages if messages is not None else []        
        
        return self   


class MessageOutboxRepository(RepositoryBase):
    
    transaction_reference:uuid4 = None
    session:Session = None   
  
    def __init__(self, session:Session, transaction_reference:uuid4):
        self.session = session
        self.transaction_reference = transaction_reference

    def get_message_by_id(self, message_id) -> MessageOutboxSchema:
        
        db_entity = self.session.query(MessageOutboxEntity).filter_by(id=message_id).first()
        
        converted:MessageOutboxSchema = None
        
        if db_entity:
            converted = MessageOutboxSchema.model_validate(db_entity)
        
        return converted
    
    def prepare_outbox_message_for_transaction(self):
        # Find all pending messages for the given transaction_id
        pending_messages = self.session.query(MessageOutboxEntity).filter_by(transaction_reference=str(self.transaction_reference), status=OutboxStatus.Pending.name).all()
        message_modified:bool = False
        
        # Update the status of each message to 'Preperation'
        for message in pending_messages:
            message.status = OutboxStatus.Preperation.name
            message_modified = True
            
        return message_modified
    
    def complete_outbox_message_in_transaction(self):
        # Find all pending messages for the given transaction_id
        pending_messages = self.session.query(MessageOutboxEntity).filter_by(transaction_reference=str(self.transaction_reference), status=OutboxStatus.Preperation.name).all()
        message_modified:bool = False
        
        # Update the status of each message to 'Ready'
        for message in pending_messages:
            message.status = OutboxStatus.Ready.name
            message_modified = True
            
        return message_modified
    
    def rollback_transaction(self):
        # Find all pending messages for the given transaction_id
        pending_messages = self.session.query(MessageOutboxEntity).filter_by(transaction_reference=str(self.transaction_reference)).all()
        message_modified:bool = False
        
        # Update the status of each message to 'Ready'
        for message in pending_messages:
            message.status = OutboxStatus.Rollback.name
            message_modified = True
            
        return message_modified
    
    
    async def add_message(self, message:MessageOutboxEntity):
        
        message.transaction_reference = str(self.transaction_reference)
        message.status = OutboxStatus.Pending.name
        message.process_count = 0
        message.is_completed = False
        
        self.session.add(message)

    async def get_next_messages(self, batch_size: int) -> ReadyForSubmissionBatch:
        
        time_threshold = datetime.utcnow() - timedelta(hours=1)
        
        ready_count = self.session.query(MessageOutboxEntity).filter(MessageOutboxEntity.status == OutboxStatus.Ready.name).count()
        not_completed_count = self.session.query(MessageOutboxEntity).filter(MessageOutboxEntity.is_completed == False).count()
        need_intervention_count = self.session.query(MessageOutboxEntity).filter(MessageOutboxEntity.status == OutboxStatus.Preperation.name).count() # MessageOutboxEntity.created_date < time_threshold and 
        
        next_messages = self.session.query(MessageOutboxEntity)\
            .filter(MessageOutboxEntity.status == OutboxStatus.Ready.name)\
            .order_by(MessageOutboxEntity.priority.desc(), MessageOutboxEntity.created_date)\
            .limit(batch_size)\
            .all()
        
        bacth_result = ReadyForSubmissionBatch().Create(messages_ready=ready_count, messages_not_completed=not_completed_count, messages=next_messages, message_needing_intervention=need_intervention_count)
        
        return bacth_result
    
    async def delete_old_message_history(self, retention_in_days:int):        
        threshold_date = datetime.utcnow() - timedelta(days=retention_in_days)
        self.session.query(MessageOutboxEntity).filter(MessageOutboxEntity.published_date < threshold_date).delete() # Can delete rollback faster
