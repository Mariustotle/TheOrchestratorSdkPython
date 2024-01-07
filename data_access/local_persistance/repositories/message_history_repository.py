from orchestrator_sdk.data_access.local_persistance.entities.message_history import MessageHistory
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timedelta

class MessageHistoryRepository:    
    session:Session = None
    
    def __init__(self, session:Session):
        self.session = session

    async def has_message_been_processed(self, message_id) -> bool:        
        return self.session.query(MessageHistory).filter_by(id=message_id).exists()
    
    async def add_message(self, message_id:uuid4):
        new_history = MessageHistory().Create(message_id=message_id, completed_date=datetime.utcnow)       
        self.session.add(new_history)

    async def delete_old_message_history(self, retention_in_days:int):        
        threshold_date = datetime.utcnow() - timedelta(days=retention_in_days)
        self.session.query(MessageHistory).filter(MessageHistory.completed_date < threshold_date).delete()
