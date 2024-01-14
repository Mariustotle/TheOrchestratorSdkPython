
from sqlalchemy import create_engine, Engine

from orchestrator_sdk.data_access.local_persistance.database_context import DatabaseContext

from sqlalchemy.ext.declarative import declarative_base
DBBase = declarative_base()

class MessageDatabase(DatabaseContext):
    
    def __init__(self) -> None:
        super().__init__(DBBase)
    
    def create_db_engine(self) -> Engine:
        return create_engine('sqlite:///message_store.db', echo=True)

message_database = MessageDatabase()