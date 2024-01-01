from typing import TypeVar, Optional, List, Type

from orchestrator_sdk.handlers.command_handlers.command_hander_base import CommandHandlerBase
from orchestrator_sdk.contracts.requests.commands.concurrent_command_request import ConcurrentCommandRequest
from orchestrator_sdk.callback_context import CallbackContext

T = TypeVar('T')
Y = TypeVar('Y')

class ConcurrentCommandHandlerBase(CommandHandlerBase[T, Y]):    
    publish_path:str = '/Commands/RegisterConcurrentCommand'    
   
    def __init__(self, processor_name:str, command_name:str, request_version:Optional[str] = None, response_version:Optional[str] = None, on_success_event_name:Optional[str] = None) -> None:
        super().__init__(processor_name=processor_name, command_name=command_name, publish_path=self.publish_path, request_version=request_version, 
                         response_version=response_version, on_success_event_name=on_success_event_name)        

    def build_request(self, request_object:T, reference:Optional[str] = None) -> ConcurrentCommandRequest:        
        serialized_payload = request_object.json()
        
        source_message_id = None
        group_trace_id = None
        if CallbackContext.is_available():
            source_message_id = CallbackContext.message_id.get()
            group_trace_id = CallbackContext.group_trace_key.get()
        
        request = ConcurrentCommandRequest().Create(
                command_name=self.command_name, command_reference=reference,
                content=serialized_payload, process_wenhook_name=self.process_webhook_name,
                dispatcher=self.processor_name, application_name=self.application_name)
        
        if (source_message_id != None):
            request.AddTracingData(source_message_id=source_message_id, group_trace_key=group_trace_id)     
        
        if (self.on_success_event_name != None and self.on_success_event_name != ''):
            request.PublishEventOnSuccess(event_name=self.on_success_event_name, event_version=self.response_version)

        # Set DeDuplicate Details after building the base request using request.AddDeDuplicationInstruction()
       
        return request     

         
    

