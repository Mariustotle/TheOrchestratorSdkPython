from orchestrator_sdk.data_access.database.entities.message_history import MessageHistory
from orchestrator_sdk.data_access.database.repository_base import RepositoryBase
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timedelta

class MessageHistoryRepository(RepositoryBase):
    
    def __init__(self, session: Session):
        super().__init__(session)

    async def has_message_been_processed(self, message_id:uuid4) -> bool:        
        found =  self.session.query(MessageHistory).filter_by(message_id=str(message_id)).first()            
        return (found != None)
    
    async def add_message(self, message_id:uuid4):
        new_history = MessageHistory().Create(message_id=message_id, completed_date=datetime.utcnow())       
        self.session.add(new_history)

    async def delete_old_message_history(self, retention_in_days:int):        
        threshold_date = datetime.utcnow() - timedelta(days=retention_in_days)
        self.query(MessageHistory).filter(MessageHistory.completed_date < threshold_date).delete()
