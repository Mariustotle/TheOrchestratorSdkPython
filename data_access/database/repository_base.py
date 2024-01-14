from abc import ABC
from sqlalchemy.orm import Session

class RepositoryBase(ABC):
    session:Session = None
    
    def __init__(self, session:Session):
        self.session = session


