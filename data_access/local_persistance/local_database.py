
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DBBase = declarative_base()

class LocalDatabase:
    db_engine:Engine = None
       
    def db_session_maker(self) -> Session:
        new_session = sessionmaker(autocommit=False, autoflush=False, bind=self.db_engine)
        return new_session()
    
    def init(self):        
        # Local database for orchestration persistance
        self.db_engine = create_engine('sqlite:///message_store.db', echo=True)
        DBBase.metadata.create_all(bind=self.db_engine)

local_database = LocalDatabase()