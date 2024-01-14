from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Engine

from abc import ABC, abstractmethod

class DatabaseContext(ABC):
    db_engine:Engine = None
    db_base = None
    
    def __init__(self, db_base) -> None:
        self.db_base = db_base
        super().__init__()
    
    def init(self) -> None:
        self.db_engine = self.create_db_engine()
        self.db_base.metadata.create_all(bind=self.db_engine)
    
    @abstractmethod
    def create_db_engine(self) -> Engine:
        pass

    def db_session_maker(self) -> Session:
        new_session = sessionmaker(autocommit=False, autoflush=False, bind=self.db_engine)
        return new_session()