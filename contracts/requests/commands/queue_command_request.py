from typing import Optional
from pydantic import BaseModel

class QueueCommandRequest(BaseModel):    
    
    ApplicationName:str = None
    CommandReference:Optional[str] = None
    QueueName:Optional[str] = None
    CommandName:str = None
    CommandVersion:Optional[str] = None
    Content: Optional[str] = None
    ProcessWebhookName:str = None
    OnSuccessWebhookName:Optional[str] = None
    SessionReference:Optional[str] = None
    RemainingQueueItems:Optional[int] = None
    DispatcherName:Optional[str] = None 
    BlockRetry:Optional[bool] = None    
    DeDuplicate:Optional[bool] = None
    UniqueInteractionHeader:Optional[str] = None

    def Create(self, 
               application_name:str,
               command_name:str,       
               process_wenhook_name: str,
               queue_name: str,               
                             
               on_success_webhook_name:Optional[str] = None,     
               de_duplicate:bool = False,
               remaining_queue_count:Optional[int] = None,               
               dispatcher_name: Optional[str] = None,
               unique_interaction_header:Optional[str] = None,
               content:Optional[str] = None,
               command_reference:Optional[str] = None,
               session_reference:Optional[str] = None,
               block_retry:Optional[str] = None,
               command_version:Optional[str] = None):       

        self.ApplicationName = application_name
        self.CommandName = command_name
        self.CommandVersion = command_version
        self.QueueName = queue_name
        self.RemainingQueueItems = remaining_queue_count
        self.CommandReference = command_reference 
        self.ProcessWebhookName = process_wenhook_name
        self.OnSuccessWebhookName = on_success_webhook_name
        self.DispatcherName = dispatcher_name
        self.Content = content
        self.SessionReference = session_reference
        self.DeDuplicate = de_duplicate
        self.UniqueInteractionHeader = unique_interaction_header
        self.BlockRetry = block_retry
        
        return self 