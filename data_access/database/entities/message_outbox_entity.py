from typing import Optional
from sqlalchemy import Column, String, DATETIME, Boolean, Integer, Index
from orchestrator_sdk.data_access.database.outbox_status import OutboxStatus
from orchestrator_sdk.data_access.database.message_entity_base import MessageEntityBase

from datetime import datetime

class MessageOutboxEntity(MessageEntityBase):
    __tablename__ = 'MessageOutbox'

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_reference = Column(String, nullable=False)
    created_date = Column(DATETIME, nullable=False)
    published_date = Column(DATETIME, nullable=True)
    publish_request_object = Column(String, nullable=True)
    status = Column(String, nullable=False)
    is_completed = Column(String, nullable=False)
    message_name = Column(String, nullable=False)
    handler_name = Column(String, nullable=False)
    de_duplication_enabled = Column(Boolean, nullable=False)
    de_duplication_delay_in_seconds = Column(Integer, nullable=True)
    unique_header_hash = Column(String, nullable=True)
    source_trace_message_id = Column(String, nullable=True)
    process_count = Column(Integer, nullable=False)
    eligible_after = Column(DATETIME, nullable=True)
    endpoint = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    
    idx_unique_header_handler = Index('idx_unique_header_handler', 'unique_header_hash', 'handler_name')
    idx_created_date = Index('idx_created_date', 'created_date')
    idx_status_priority_created = Index('idx_status_priority_created', 'status', 'priority', 'created_date', postgresql_using='btree')
    
    @staticmethod
    def Create( 
            publish_request_object:object,
            endpoint:str,
            handler_name:str,
            message_name:str,
            source_trace_message_id:str,
            de_duplication_enabled:bool,            
            unique_header_hash:Optional[str],
            priority:Optional[int],
            de_duplication_delay_in_seconds:Optional[int] = None,
            eligible_after:Optional[datetime] = None):      
        
        return MessageOutboxEntity(
            publish_request_object = publish_request_object.json() if publish_request_object is not None else None,
            status = str(OutboxStatus.Pending.name),
            message_name = message_name,
            handler_name = handler_name,
            source_trace_message_id = source_trace_message_id,
            process_count = 0,
            de_duplication_enabled = de_duplication_enabled,
            de_duplication_delay_in_seconds = de_duplication_delay_in_seconds,
            unique_header_hash = unique_header_hash,
            eligible_after = eligible_after,
            created_date = datetime.utcnow(),
            is_completed = str(False),
            published_date = None,
            endpoint = endpoint,
            priority = priority if priority is not None else 10
        )  
