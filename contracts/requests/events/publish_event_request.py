from typing import Optional
from pydantic import BaseModel, UUID4

class PublishEventRequest(BaseModel):    
    
    ApplicationName:str 
    EventName:str
    EventVersion:Optional[str] = None
    EventReference:Optional[str] = None
    Content:Optional[str] = None
    Priority:Optional[int] = None
    UniqueRequestHeader: Optional[str] = None
    SourceTraceMessageId: Optional[UUID4] = None
    
    @staticmethod
    def Create (
            application_name:str,
            event_name:str,            
            priority:Optional[int] = None,
            content:Optional[str] = None,
            event_reference:Optional[str] = None,
            event_version:Optional[str] = None,
            source_trace_message_id:Optional[UUID4] = None,
            unique_request_header:Optional[str] = None):     
        
        return PublishEventRequest(
            ApplicationName = application_name,
            EventName = event_name,
            EventVersion = event_version,
            EventReference = event_reference,
            Content = content,
            Priority = priority,
            SourceTraceMessageId = source_trace_message_id,
            UniqueRequestHeader=unique_request_header
        )

