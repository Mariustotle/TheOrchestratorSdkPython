from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict

class OutboxSummary(BaseModel):
    TotalItemsPendingSubmission: int
    TotalItemsReadyForSubmission: int
    OldestItem: Optional[datetime]
    LatestItem: Optional[datetime]
    DetachedMessages: int
    PendingMessages: Dict[str, int]

    @staticmethod
    def Create(total_items_pending_submission:int, total_items_ready_for_submission:int, 
               detached_messages:int, pending_messages:Dict[str, int], oldest_item:Optional[datetime], latest_item:Optional[datetime]) -> 'OutboxSummary':

        return OutboxSummary (
            TotalItemsPendingSubmission = total_items_pending_submission,
            TotalItemsReadyForSubmission = total_items_ready_for_submission,
            DetachedMessages = detached_messages,
            PendingMessages = pending_messages,
            OldestItem=oldest_item,
            LatestItem=latest_item
        )

