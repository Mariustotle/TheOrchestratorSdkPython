
from typing import Optional
from pydantic import BaseModel, UUID4

from orchestrator_sdk.contracts.requests.common.de_duplication_details import DeDuplicationDetails

class PublishEventRequest(BaseModel):    
    
    ApplicationName:str = None
    EventName:str = None
    EventVersion:Optional[str] = None
    EventReference:Optional[str] = None
    Content:Optional[str] = None
    Priority:Optional[int] = None
    UniqueInteractionHeader: Optional[str] = None
    SourceTraceMessageId: UUID4 = None
    
    def Create(self, 
               application_name:str,
               event_name:str,            
               priority:Optional[int] = None,
               content:Optional[str] = None,
               event_reference:Optional[str] = None,
               event_version:Optional[str] = None,
               source_trace_message_id:Optional[UUID4] = None):       

        self.ApplicationName = application_name
        self.EventName = event_name
        self.EventVersion = event_version
        self.EventReference = event_reference
        self.Content = content
        self.Priority = priority
        self.SourceTraceMessageId = source_trace_message_id
        
        return self