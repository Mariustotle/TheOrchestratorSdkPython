import uuid

from typing import Optional
from pydantic import BaseModel

class PublishEventRequest(BaseModel):    
    
    ApplicationName:str 
    EventName:str
    EventVersion:Optional[str] = None
    EventReference:Optional[str] = None
    Content:Optional[str] = None
    Priority:Optional[int] = None
    UniqueRequestHeaderHash: Optional[str] = None
    SourceTraceMessageId: Optional[str] = None
    SourceMapMessageId: Optional[str] = None
    ItemsRemainingAtSource: Optional[int] = None
    
    @staticmethod
    def Create (
            application_name:str,
            event_name:str,
            items_at_source:Optional[int] = None,
            priority:Optional[int] = None,
            content:Optional[str] = None,
            event_reference:Optional[str] = None,
            event_version:Optional[str] = None,
            source_trace_message_id:Optional[str] = None,
            source_map_message_id:Optional[str] = None,
            unique_request_header_hash:Optional[str] = None):     
        
        return PublishEventRequest(
            ApplicationName = application_name,
            EventName = event_name,
            EventVersion = event_version,
            EventReference = event_reference,
            Content = content,
            ItemsRemainingAtSource=items_at_source,
            Priority = priority,
            SourceTraceMessageId = source_trace_message_id,
            SourceMapMessageId = source_map_message_id,
            UniqueRequestHeaderHash = unique_request_header_hash
        )

