from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from uuid import UUID
from orchestrator_sdk.callback.processing_context import ProcessingContext
from orchestrator_sdk.contracts.requests.batch_context import BatchContext

class PublishEventRequest(BaseModel):    
    
    ApplicationName:str 
    EventName:str
    EventVersion:Optional[str] = None
    EventReference:Optional[str] = None
    Content:Optional[str] = None
    Priority:Optional[int] = None
    UniqueRequestHeaderHash: Optional[str] = None
    GroupTraceKey: Optional[UUID] = None
    SourceMapMessageId: Optional[UUID] = None
    OutboxReferenceId: Optional[str] = None
    RequestDate:Optional[datetime] = None
    SubmissionBatch: Optional[BatchContext] = None

    
    @staticmethod
    def Create (
            processing_context:ProcessingContext,
            application_name:str,
            event_name:str,
            priority:Optional[int] = None,
            content:Optional[str] = None,
            event_reference:Optional[str] = None,
            event_version:Optional[str] = None,
            unique_request_header_hash:Optional[str] = None       
            ):     
        
        return PublishEventRequest(
            ApplicationName = application_name,
            EventName = event_name,
            EventVersion = event_version,
            EventReference = event_reference,
            Content = content,
            GroupTraceKey = processing_context.group_trace_key,
            SourceMapMessageId = processing_context.source_map_message_id,
            Priority = priority,
            UniqueRequestHeaderHash = unique_request_header_hash
        )

