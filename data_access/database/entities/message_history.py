from sqlalchemy import Column, String, DATETIME
from orchestrator_sdk.data_access.database.message_entity_base import MessageEntityBase

from datetime import datetime
from uuid import uuid4
import json

class MessageHistory(MessageEntityBase):
    __tablename__ = 'MessageHistory'

    message_id = Column(String, nullable=False)
    completed_date = Column(DATETIME, nullable=False)    
   
    def Create(self, 
               message_id:uuid4,
               completed_date:datetime):       

        self.message_id = str(message_id)
        self.completed_date = completed_date
                
        return self 

