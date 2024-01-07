from orchestrator_sdk.data_access.local_persistance.entities.message_history import MessageHistory
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timedelta

class MessageHistoryRepository:        

    async def has_message_been_processed(self, message_id:uuid4, session:Session) -> bool:        
        found =  session.query(MessageHistory).filter_by(message_id=str(message_id)).first()            
        return (found != None)
    
    async def add_message(self, message_id:uuid4, session:Session):
        new_history = MessageHistory().Create(message_id=message_id, completed_date=datetime.utcnow())       
        session.add(new_history)

    async def delete_old_message_history(self, retention_in_days:int, session:Session):        
        threshold_date = datetime.utcnow() - timedelta(days=retention_in_days)
        session.query(MessageHistory).filter(MessageHistory.completed_date < threshold_date).delete()
