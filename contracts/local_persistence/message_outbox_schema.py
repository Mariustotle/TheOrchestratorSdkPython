from orchestrator_sdk.data_access.database.outbox_status import OutboxStatus
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from datetime import datetime
from uuid import UUID, uuid4


class MessageOutboxSchema(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    transaction_reference: UUID
    created_date: datetime
    publish_request_object: str
    status: OutboxStatus
    is_completed: bool
    handler: str
    source_trace_message_id: Optional[str] = None
    process_count: int
    eligible_after: Optional[datetime]

