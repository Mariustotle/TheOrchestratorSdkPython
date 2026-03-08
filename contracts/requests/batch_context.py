from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class BatchContext(BaseModel):

    BatchId: UUID
    TotalItemsInBatch: int
    PositionInBatch: int
    TotalRemainingExcludingBatch: int
    OldestRemainingItem: Optional[datetime] = None

    @staticmethod
    def Create(batch_id: UUID, total_items_in_batch: int, position_in_batch: int, total_remaining_excluding_batch: int, oldest_remaining_item: Optional[datetime] = None):
       
        return BatchContext(
            BatchId = batch_id,
            TotalItemsInBatch = total_items_in_batch,
            PositionInBatch = position_in_batch,
            TotalRemainingExcludingBatch = total_remaining_excluding_batch,
            OldestRemainingItem = oldest_remaining_item
        )