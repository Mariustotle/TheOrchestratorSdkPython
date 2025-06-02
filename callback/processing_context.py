from pydantic import BaseModel
from typing import Optional

class ProcessingContext(BaseModel):
    source_message_trace_id:Optional[str] = None
    source_priority:Optional[int] = None
    message_name:str = None
    reference:Optional[str] = None

    @staticmethod
    def Create(source_message_trace_id:Optional[str], source_priority:Optional[int], message_name:str, reference:Optional[str]):   
        return ProcessingContext(
            source_message_trace_id = source_message_trace_id,
            source_priority = source_priority,
            message_name=message_name,
            reference=reference
        )