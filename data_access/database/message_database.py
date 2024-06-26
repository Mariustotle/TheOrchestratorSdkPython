
from sqlalchemy import create_engine, Engine
from datetime import datetime, timedelta

from orchestrator_sdk.data_access.database.database_context import DatabaseContext

from sqlalchemy.orm import declarative_base
DBBase = declarative_base()

class MessageDatabase(DatabaseContext):
    
    last_cleanup_timestamp:datetime = None
    
    def __init__(self) -> None:
        super().__init__(DBBase)
    
    def create_db_engine(self) -> Engine:
        return create_engine('sqlite:///message_store.db', echo=False, pool_size=10, max_overflow=20)

message_database = MessageDatabase()