from orchestrator_sdk.data_access.local_persistance.outbox_status import OutboxStatus
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from datetime import datetime
from uuid import uuid4


class MessageOutboxSchema(BaseModel):
    id: uuid4
    transaction_reference: uuid4
    created_date: datetime
    publish_request_object: str
    status: OutboxStatus
    is_completed: bool
    handler: str
    source_message_id: Optional[str] = None
    group_trace_key: Optional[str] = None
    process_count: int
    eligible_after: Optional[datetime]

    class Config:
        from_attributes = True
