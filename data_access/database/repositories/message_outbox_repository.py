from orchestrator_sdk.data_access.database.entities.message_outbox_entity import MessageOutboxEntity
from orchestrator_sdk.contracts.local_persistence.message_outbox_schema import MessageOutboxSchema
from orchestrator_sdk.data_access.database.outbox_status import OutboxStatus
from orchestrator_sdk.data_access.database.repository_base import RepositoryBase
from orchestrator_sdk.contracts.health.outbox_summary import OutboxSummary
from sqlalchemy import and_, func, or_

from sqlalchemy.orm import Session
from uuid import uuid4
from typing import List, Dict
from datetime import datetime, timedelta, timezone

class ReadyForSubmissionBatch():
    messages_ready:int
    messages_not_completed:int
    messages_needing_intervention:int
    messages:List[MessageOutboxEntity]
    
    def __init__(self, messages_ready:int,
            messages_not_completed:int,
            messages_needing_intervention:int,
            messages:List[MessageOutboxEntity]) -> None:
        
        self.messages_ready = messages_ready
        self.messages_not_completed =messages_not_completed
        self.messages_needing_intervention = messages_needing_intervention
        self.messages = messages  


class MessageOutboxRepository(RepositoryBase):
    
    transaction_reference:uuid4 = None
    session:Session = None   
  
    def __init__(self, session:Session, transaction_reference:uuid4):
        self.session = session
        self.transaction_reference = transaction_reference

    def get_message_by_id(self, trace_message_id) -> MessageOutboxSchema:
        
        db_entity = self.session.query(MessageOutboxEntity).filter_by(id=trace_message_id).first()
        
        converted:MessageOutboxSchema = None
        
        if db_entity:
            converted = MessageOutboxSchema.model_validate(db_entity)
        
        return converted
    
    def get_pending_message_counts(self) -> dict:
        
        remaining_messages = (
            self.session.query(
                MessageOutboxEntity.message_name,
                func.count(MessageOutboxEntity.id).label('remaining_count')
            )
            .filter(MessageOutboxEntity.is_completed == False) 
            .group_by(MessageOutboxEntity.message_name)
            .all())
        
        remaining_message_dict = {name: count for name, count in remaining_messages}        
        return remaining_message_dict     
        
    
    def prepare_outbox_message_for_transaction(self):
        # Find all pending messages for the given transaction_id
        pending_messages = self.session.query(MessageOutboxEntity).filter_by(transaction_reference=str(self.transaction_reference), status=OutboxStatus.Pending.name).all()
        message_modified:bool = False
        
        # Update the status of each message to 'Preperation'
        for message in pending_messages:
            message.status = OutboxStatus.Preparation.name
            message_modified = True
            
        return message_modified
    
    def complete_outbox_message_in_transaction(self):
        # Find all pending messages for the given transaction_id
        pending_messages = self.session.query(MessageOutboxEntity).filter_by(transaction_reference=str(self.transaction_reference), status=OutboxStatus.Preparation.name).all()
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
        
        if (message.de_duplication_enabled and message.de_duplication_delay_in_seconds > 0):
            time_delta = timedelta(minutes=message.de_duplication_delay_in_seconds)
            message.eligible_after = datetime.utcnow() + time_delta
        
        self.session.add(message)
        
    async def remove_duplicates_pending_submission(self):
        
        # Step 1: Identify the most recent records for each unique_header_hash and handler_name
        subquery = self.session.query(
            MessageOutboxEntity.unique_header_hash,
            MessageOutboxEntity.handler_name,
            func.max(MessageOutboxEntity.created_date).label('latest_date')
        ).group_by(
            MessageOutboxEntity.unique_header_hash,
            MessageOutboxEntity.handler_name
        ).subquery()
                
        # Step 2: Update the older duplicate records
        duplicates = self.session.query(MessageOutboxEntity).join(
            subquery,
            (MessageOutboxEntity.unique_header_hash == subquery.c.unique_header_hash) &
            (MessageOutboxEntity.handler_name == subquery.c.handler_name) &
            (MessageOutboxEntity.created_date < subquery.c.latest_date)
        )

        for record in duplicates:
            record.status = OutboxStatus.Duplicate.name
            record.is_completed = True

        self.session.commit()
                

    async def get_next_messages(self, batch_size: int) -> ReadyForSubmissionBatch:
       
        ready_count = self.session.query(MessageOutboxEntity).filter(MessageOutboxEntity.status == OutboxStatus.Ready.name,
                (MessageOutboxEntity.eligible_after == None) | (MessageOutboxEntity.eligible_after < datetime.utcnow())).count()
        not_completed_count = self.session.query(MessageOutboxEntity).filter(MessageOutboxEntity.is_completed == False).count()
        need_intervention_count = self.session.query(MessageOutboxEntity).filter(MessageOutboxEntity.status == OutboxStatus.Preparation.name).count() 
        
        next_messages = self.session.query(MessageOutboxEntity)\
            .filter(
                MessageOutboxEntity.status == OutboxStatus.Ready.name,
                (MessageOutboxEntity.eligible_after == None) | (MessageOutboxEntity.eligible_after < datetime.utcnow())
            )\
            .order_by(MessageOutboxEntity.priority.desc(), MessageOutboxEntity.created_date)\
            .limit(batch_size)\
            .all()
            
        messages = next_messages if next_messages is not None else List[MessageOutboxEntity]
        
        bacth_result = ReadyForSubmissionBatch(messages_ready=ready_count, messages_not_completed=not_completed_count,
             messages_needing_intervention=need_intervention_count, messages=messages)
        
        return bacth_result
    
    async def delete_old_message_history(self, session:Session):        
        session.query(MessageOutboxEntity).filter(MessageOutboxEntity.is_completed == True).delete()

    async def get_outbox_summary_async(self) -> OutboxSummary:
        now = datetime.utcnow()

        rows = (
            self.session
                .query(MessageOutboxEntity.message_name,
                    func.count().label("cnt"))
                .filter(MessageOutboxEntity.is_completed == False)
                .group_by(MessageOutboxEntity.message_name)
                .all()
        )
        remaining_messages = {name: cnt for name, cnt in rows}

        ready_for_submission = (
            self.session
                .query(func.count())
                .filter(
                    MessageOutboxEntity.is_completed == False,
                    or_(
                        MessageOutboxEntity.status == OutboxStatus.Ready.name,
                        and_(
                            MessageOutboxEntity.status == OutboxStatus.Retry.name,
                            or_(
                                MessageOutboxEntity.eligible_after.is_(None),
                                MessageOutboxEntity.eligible_after < now,
                            )
                        ),
                    )
                )
                .scalar() 
        )

        detached_messages = (
            self.session
                .query(func.count())
                .filter(MessageOutboxEntity.status ==
                        OutboxStatus.Preparation.name)
                .scalar()
        )

        return OutboxSummary.Create(
            pending_messages                    = remaining_messages,
            total_items_ready_for_submission    = ready_for_submission,
            detached_messages                   = detached_messages,
            total_items_pending_submission      = sum(remaining_messages.values())
        )


