from typing import TypeVar, Optional, List

from orchestrator_sdk.handlers.command_handlers.command_hander_base import CommandHandlerBase
from orchestrator_sdk.contracts.requests.commands.concurrent_command_request import ConcurrentCommandRequest
from orchestrator_sdk.callback_context import CallbackContext

import json

T = TypeVar('T')
Y = TypeVar('Y')

class ConcurrentCommandHandlerBase(CommandHandlerBase[T, Y]):
    
    publish_path:str = '/Commands/RegisterConcurrentCommand'    
   
    def __init__(self, processor_name:str, message_name:str, process_request_type, on_success_class_type, 
                 use_success_webhook:bool = False) -> None:
        super().__init__(processor_name=processor_name, message_name=message_name, process_request_type=process_request_type, on_success_class_type=on_success_class_type,
                         use_success_webhook=use_success_webhook, publish_path=self.publish_path)
        
        
    def build_request(self, request_object:T, reference:Optional[str] = None) -> ConcurrentCommandRequest:        
        serialized_payload = request_object.json()
        
        source_message_id = None
        group_trace_id = None
        if CallbackContext.is_available():
            source_message_id = CallbackContext.message_id.get()
            group_trace_id = CallbackContext.group_trace_key.get()
        
        request = ConcurrentCommandRequest().Create(
                command_name=self.message_name, command_reference=reference,
                content=serialized_payload, process_wenhook_name=self.process_webhook_name,
                on_success_webhook_name=self.on_success_webhook_name, 
                dispatcher=self.processor_name, application_name=self.application_name, source_message_id=source_message_id, group_trace_key=group_trace_id)
       
        return request     

         
    

