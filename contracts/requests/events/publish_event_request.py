
from typing import Optional
from pydantic import BaseModel, UUID4

class PublishEventRequest(BaseModel):    
    
    ApplicationName:str = None
    EventName:str = None
    EventVersion:Optional[str] = None
    EventReference:Optional[str] = None
    Content:Optional[str] = None
    SourceMessageId:Optional[UUID4] = None,
    GroupTraceKey: Optional[UUID4] = None
    Priority:Optional[int] = None
    DeDuplicate:bool = None
    UniqueInteractionHeader: Optional[str] = None
    
    def Create(self, 
               application_name:[str],
               event_name:[str],            
               de_duplicate:bool = False,
               unique_interaction_header:Optional[str] = None,
               priority:Optional[int] = None,
               content:Optional[str] = None,
               event_reference:Optional[str] = None,
               source_message_id:Optional[UUID4] = None,
               group_trace_id:Optional[UUID4] = None,
               event_version:Optional[str] = None):       

        self.ApplicationName = application_name
        self.EventName = event_name
        self.EventVersion = event_version
        self.EventReference = event_reference
        self.Content = content
        self.SourceMessageId = source_message_id
        self.GroupTraceKey = group_trace_id
        self.Priority = priority
        self.DeDuplicate = de_duplicate
        self.UniqueInteractionHeader = unique_interaction_header
        
        return self 
    
    