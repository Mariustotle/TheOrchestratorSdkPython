from sqlalchemy import Column, String, DATETIME
from orchestrator_sdk.data_access.database.message_entity_base import MessageEntityBase

from datetime import datetime
from uuid import uuid4

class MessageHistory(MessageEntityBase):
    __tablename__ = 'MessageHistory'

    message_id = Column(String, nullable=False)
    completed_date = Column(DATETIME, nullable=False)    
   
    @staticmethod
    def Create( 
            message_id:uuid4,
            completed_date:datetime):
        
        return MessageHistory(                
            message_id = str(message_id),
            completed_date = completed_date
        )
