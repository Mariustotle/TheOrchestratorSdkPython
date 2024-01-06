from orchestrator_sdk.data_access.local_persistance.entities.message_outbox_entity import MessageOutboxEntity
from orchestrator_sdk.contracts.local_persistence.message_outbox_schema import MessageOutboxSchema
from orchestrator_sdk.data_access.local_persistance.outbox_status import OutboxStatus
from sqlalchemy.orm import Session
from uuid import uuid4
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
    
    def commit(self):
        # Find all pending messages for the given transaction_id
        pending_messages = self.session.query(MessageOutboxEntity).filter_by(transaction_reference=str(self.transaction_reference), status=OutboxStatus.Pending.name).all()

        # Update the status of each message to 'Ready'
        for message in pending_messages:
            message.status = OutboxStatus.Ready.name
    
    
    def add_message(self, message:MessageOutboxEntity):
        
        message.transaction_reference = str(self.transaction_reference)
        message.status = OutboxStatus.Pending.name
        message.process_count = 0
        message.is_completed = False
        
        self.session.add(message)

    def get_next_messages(self, batch_size: int):
        messages = self.session.query(MessageOutboxEntity)\
            .filter_by(status=OutboxStatus.Ready.name)\
            .limit(batch_size)\
            .all()
        
        return [MessageOutboxSchema.model_validate(message) for message in messages]