from typing import Optional
from pydantic import BaseModel

from uuid import UUID
from orchestrator_sdk.callback.processing_context import ProcessingContext

class PublishEventRequest(BaseModel):    
    
    ApplicationName:str 
    EventName:str
    EventVersion:Optional[str] = None
    EventReference:Optional[str] = None
    Content:Optional[str] = None
    Priority:Optional[int] = None
    UniqueRequestHeaderHash: Optional[str] = None
    GroupTraceKey: Optional[UUID] = None
    SourceTraceMessageId: Optional[UUID] = None
    SourceMapMessageId: Optional[UUID] = None
    ItemsRemainingAtSource: Optional[int] = None
    
    @staticmethod
    def Create (
            processing_context:ProcessingContext,
            application_name:str,
            event_name:str,
            items_at_source:Optional[int] = None,
            priority:Optional[int] = None,
            content:Optional[str] = None,
            event_reference:Optional[str] = None,
            event_version:Optional[str] = None,
            unique_request_header_hash:Optional[str] = None):     
        
        return PublishEventRequest(
            ApplicationName = application_name,
            EventName = event_name,
            EventVersion = event_version,
            EventReference = event_reference,
            Content = content,
            ItemsRemainingAtSource = items_at_source,
            GroupTraceKey = processing_context.group_trace_key,
            SourceMapMessageId = processing_context.source_map_message_id,
            SourceTraceMessageId = processing_context.source_message_trace_id,
            Priority = priority,
            UniqueRequestHeaderHash = unique_request_header_hash
        )

