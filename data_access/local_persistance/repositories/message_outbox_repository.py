from orchestrator_sdk.data_access.local_persistance.entities.message_outbox_entity import MessageOutboxEntity
from orchestrator_sdk.contracts.local_persistence.message_outbox_schema import MessageOutboxSchema
from orchestrator_sdk.data_access.local_persistance.outbox_status import OutboxStatus
from sqlalchemy.orm import Session
from uuid import uuid4
from typing import List

from datetime import datetime, timedelta


class ReadyForSubmissionBatch:
    messages_ready:int = None
    messages_not_completed:int = None
    messages:List[MessageOutboxEntity] = None
    
    def Create(self, 
        messages_ready:int,
        messages_not_completed:int,
        messages:[MessageOutboxEntity] = None):
        
        self.messages_ready = messages_ready
        self.messages_not_completed = messages_not_completed
        self.messages = messages if messages is not None else []        
        
        return self   


class MessageOutboxRepository:
    
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
        added_messages:bool = False
        
        # Update the status of each message to 'Preperation'
        for message in pending_messages:
            message.status = OutboxStatus.Preperation.name
            added_messages = True
            
        return added_messages
    
    def complete_outbox_message_in_transaction(self):
        # Find all pending messages for the given transaction_id
        pending_messages = self.session.query(MessageOutboxEntity).filter_by(transaction_reference=str(self.transaction_reference), status=OutboxStatus.Preperation.name).all()
        added_messages:bool = False
        
        # Update the status of each message to 'Ready'
        for message in pending_messages:
            message.status = OutboxStatus.Ready.name
            added_messages = True
            
        return added_messages
    
    
    async def add_message(self, message:MessageOutboxEntity):
        
        message.transaction_reference = str(self.transaction_reference)
        message.status = OutboxStatus.Pending.name
        message.process_count = 0
        message.is_completed = False
        
        self.session.add(message)

    async def get_next_messages(self, batch_size: int) -> ReadyForSubmissionBatch:
        
        ready_count = self.session.query(MessageOutboxEntity).filter(MessageOutboxEntity.status == OutboxStatus.Ready.name).count()
        not_completed_count = self.session.query(MessageOutboxEntity).filter(MessageOutboxEntity.is_completed == False).count()
        
        next_messages = self.session.query(MessageOutboxEntity)\
            .filter(MessageOutboxEntity.status == OutboxStatus.Ready.name)\
            .order_by(MessageOutboxEntity.created_date)\
            .limit(batch_size)\
            .all()
        
        '''
        
        #or (MessageOutboxEntity.status == OutboxStatus.Retry.name and MessageOutboxEntity.eligible_after is not None and MessageOutboxEntity.eligible_after < datetime.utcnow())
        next_messages =  self.session.query(MessageOutboxEntity)\
            .filter(MessageOutboxEntity.status == OutboxStatus.Ready.name)\
            .limit(batch_size)\
            .order_by(MessageOutboxEntity.created_date)\
            .all() 
            
        '''  
        
        bacth_result = ReadyForSubmissionBatch().Create(messages_ready=ready_count, messages_not_completed=not_completed_count, messages=next_messages)
        
        return bacth_result
    
    async def delete_old_message_history(self, retention_in_days:int):        
        threshold_date = datetime.utcnow() - timedelta(days=retention_in_days)
        self.session.query(MessageOutboxEntity).filter(MessageOutboxEntity.published_date < threshold_date).delete()
