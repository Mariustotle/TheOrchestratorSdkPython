from sqlalchemy import Column, String, DATETIME, Boolean, Integer
from orchestrator_sdk.data_access.database.outbox_status import OutboxStatus
from orchestrator_sdk.data_access.database.message_entity_base import MessageEntityBase

from datetime import datetime
from uuid import uuid4
import json

class MessageOutboxEntity(MessageEntityBase):
    __tablename__ = 'MessagesOutbox'

    transaction_reference = Column(String, nullable=False)
    created_date = Column(DATETIME, nullable=False)
    published_date = Column(DATETIME, nullable=True)
    publish_request_object = Column(String, nullable=True)
    status = Column(String, nullable=False)
    is_completed = Column(String, nullable=False)
    handler_name = Column(String, nullable=False)
    source_trace_message_id = Column(String, nullable=True)
    process_count = Column(Integer, nullable=False)
    eligible_after = Column(DATETIME, nullable=True)
    endpoint = Column(String, nullable=False)
    priority = Column(Integer, nullable=True)
    
    def Create(self, 
               publish_request_object:object,
               endpoint:str,
               handler_name:str,
               source_trace_message_id:str,
               priority:int):       

        self.publish_request_object = publish_request_object.json() if publish_request_object is not None else None
        self.status = str(OutboxStatus.Pending.name)
        self.handler_name = handler_name
        self.source_trace_message_id = source_trace_message_id
        self.process_count = 0
        self.eligible_after = None
        self.created_date = datetime.utcnow()
        self.is_completed = str(False)
        self.published_date = None
        self.endpoint = endpoint
        self.priority = priority
                
        return self 

