from orchestrator_sdk.data_access.database.outbox_status import OutboxStatus
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
    source_message_trace_id: Optional[str] = None
    process_count: int
    eligible_after: Optional[datetime]

