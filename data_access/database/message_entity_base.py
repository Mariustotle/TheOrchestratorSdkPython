from sqlalchemy import Column, String
from orchestrator_sdk.data_access.database.message_database import DBBase
import uuid

class MessageEntityBase(DBBase):
    __abstract__ = True
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    class Config:
        from_attributes = True
