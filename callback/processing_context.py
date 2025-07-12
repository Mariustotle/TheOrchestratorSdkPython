from pydantic import BaseModel
from typing import Optional

from uuid import UUID

class ProcessingContext(BaseModel):
    source_message_trace_id:Optional[UUID] = None
    source_map_message_id:Optional[UUID] = None
    group_trace_key:Optional[UUID] = None
    source_priority:Optional[int] = None
    message_name:str = None
    reference:Optional[str] = None

    @staticmethod
    def Create(source_message_trace_id:Optional[UUID], source_map_message_id:Optional[UUID], source_priority:Optional[int], group_trace_key:Optional[UUID], message_name:str, reference:Optional[str]):   
        return ProcessingContext(
            source_map_message_id = source_map_message_id,
            source_message_trace_id = source_message_trace_id,
            source_priority = source_priority,
            group_trace_key = group_trace_key,
            message_name=message_name,
            reference=reference
        )