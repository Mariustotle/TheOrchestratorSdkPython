from typing import TypeVar, Optional, List
from orchestrator_sdk.handlers.command_handlers.command_hander_base import CommandHandlerBase
from orchestrator_sdk.contracts.requests.commands.queue_command_request import QueueCommandRequest

import json

T = TypeVar('T')
Y = TypeVar('Y')

class QueueCommandHandlerBase(CommandHandlerBase[T, Y]):
    
    publish_path:str = '/Commands/RegisterQueueCommand'
    queue_name:str 
   
    def __init__(self, processor_name:str, queue_name:str, message_name:str, process_request_type, on_success_class_type, 
                 use_success_webhook:bool = False) -> None:
        super().__init__(processor_name=processor_name, message_name=message_name, process_request_type=process_request_type, on_success_class_type=on_success_class_type,
                         use_success_webhook=use_success_webhook, publish_path=self.publish_path)
        self.queue_name = queue_name
        
    def build_request(self, command_name:str, payload:T, client_reference:Optional[str] = None) -> QueueCommandRequest:     
        
        serialized_payload = payload.json()
        
        request = QueueCommandRequest().Create(
                queue_name=self.queue_name, command_name=command_name, command_reference=client_reference,
                content=serialized_payload, process_wenhook_name=self.process_webhook_name, 
                on_success_webhook_name=self.on_success_webhook_name, dispatcher_name=self.processor_name,
                application_name=self.application_name)
        
        return request     
       
    
         
    

