
from typing import Optional
from pydantic import BaseModel, UUID4

from orchestrator_sdk.contracts.requests.common.de_duplication_details import DeDuplicationDetails
from orchestrator_sdk.contracts.requests.common.tracing_data import TracingData

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
    
    DeDuplicationDetails:Optional[DeDuplicationDetails] = None
    TracingData:Optional[TracingData] = None
    
    def Create(self, 
               application_name:[str],
               event_name:[str],            
               priority:Optional[int] = None,
               content:Optional[str] = None,
               event_reference:Optional[str] = None,
               event_version:Optional[str] = None):       

        self.ApplicationName = application_name
        self.EventName = event_name
        self.EventVersion = event_version
        self.EventReference = event_reference
        self.Content = content
        self.Priority = priority
        
        return self     
   
    def AddTracingData(self,
            source_message_id:UUID4,
            group_trace_key:Optional[UUID4] = None):
        
        self.TracingData = TracingData().Create(source_message_id=source_message_id, group_trace_id=group_trace_key)
        return self
    
    def AddDeDuplicationInstruction(self,
            unique_interaction_header:Optional[str] = None):
        
        self.DeDuplicationDetails = DeDuplicationDetails().Create(de_duplicate=True, unique_interaction_header=unique_interaction_header)
        return self