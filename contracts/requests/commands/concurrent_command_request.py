from typing import Optional
from pydantic import BaseModel, UUID4

from orchestrator_sdk.contracts.requests.common.de_duplication_details import DeDuplicationDetails
from orchestrator_sdk.contracts.requests.common.success_event_details import SuccessEventDetails

class ConcurrentCommandRequest(BaseModel):    
    
    Dispatcher: Optional[str] = None 
    BlockRetry:Optional[bool] = None
    ApplicationName:str = None
    CommandReference: Optional[str] = None
    CommandName: str = None
    CommandVersion: Optional[str] = None
    Content: Optional[str] = None
    ProcessWebhookName: str = None
    Priority:Optional[int] = None
    
    DeDuplicationDetails:Optional[DeDuplicationDetails] = None
    SuccessEventDetails:Optional[SuccessEventDetails] = None
    SourceTraceMessageId: UUID4 = None

    def Create(self, 
               application_name:str,
               command_name:str,       
               process_wenhook_name: str,     
               dispatcher: Optional[str] = None,
               
               priority:Optional[int] = None,
               content:Optional[str] = None,
               command_reference:Optional[str] = None,

               block_retry:Optional[str] = None,
               command_version:Optional[str] = None,
               source_trace_message_id: UUID4 = None):       

        self.ApplicationName = application_name
        self.CommandName = command_name
        self.CommandVersion = command_version
        self.CommandReference = command_reference 
        self.ProcessWebhookName = process_wenhook_name
        self.Dispatcher = dispatcher
        self.Content = content
        self.Priority = priority
        self.BlockRetry = block_retry      
        self.SourceTraceMessageId = source_trace_message_id
        
        return self 
    
    def PublishEventOnSuccess(self,
            event_name:str,
            event_version:str):
        
        self.SuccessEventDetails = SuccessEventDetails().Create(event_name=event_name, event_version=event_version)        
        return self    
   
    def AddDeDuplicationInstruction(self,
            unique_interaction_header:Optional[str] = None):
        
        self.DeDuplicationDetails = DeDuplicationDetails().Create(de_duplicate=True, unique_interaction_header=unique_interaction_header)
        return self