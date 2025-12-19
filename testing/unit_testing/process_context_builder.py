from orchestrator_sdk.callback.processing_context import ProcessingContext
from typing import Optional

from uuid import UUID
import uuid

class ProcessContextBuilder() : 
    source_map_message_id:Optional[UUID] = None
    group_trace_key:Optional[UUID] = None
    source_priority:Optional[int] = None
    message_name:str = None
    reference:Optional[str] = None

    def __init__(self, message_name:str, source_map_message_id:Optional[UUID] = None, 
                 source_priority:Optional[int] = None, reference:Optional[str] = None, group_trace_key:Optional[UUID] = None):
        
        self.message_name = message_name
        self.source_map_message_id = source_map_message_id
        self.group_trace_key = group_trace_key
        self.source_priority = source_priority if source_priority != None else 10
        self.reference = reference

    def set_reference(self, reference:str) -> 'ProcessContextBuilder':
        self.reference = reference
        return self

    def build(self) -> 'ProcessingContext':
        return ProcessingContext.Create(message_name=self.message_name, source_map_message_id=self.source_map_message_id,
                source_priority=self.source_priority, reference=self.reference,
                group_trace_key=self.group_trace_key) 
