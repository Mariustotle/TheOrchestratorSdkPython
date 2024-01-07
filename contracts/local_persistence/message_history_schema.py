from orchestrator_sdk.data_access.local_persistance.outbox_status import OutboxStatus
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4

class MessageHistorySchema(BaseModel):
    id: uuid4
    message_id: uuid4
    completed_date: datetime

    class Config:
        from_attributes = True
