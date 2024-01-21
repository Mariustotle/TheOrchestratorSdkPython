from typing import TypeVar, Optional

from orchestrator_sdk.handlers.command_handlers.command_hander_base import CommandHandlerBase
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope
from orchestrator_sdk.contracts.requests.commands.concurrent_command_request import ConcurrentCommandRequest
from orchestrator_sdk.callback_context import CallbackContext

T = TypeVar('T')
Y = TypeVar('Y')

class ConcurrentCommandHandlerBase(CommandHandlerBase[T, Y]):    
    publish_path:str = '/Commands/RegisterConcurrentCommand'    
   
    def __init__(self, processor_name:str, command_name:str, request_type:type, response_type:type, request_version:Optional[str] = None, response_version:Optional[str] = None, on_success_event_name:Optional[str] = None) -> None:
        super().__init__(processor_name=processor_name, command_name=command_name, publish_path=self.publish_path, request_type=request_type, response_type=response_type, request_version=request_version, 
                         response_version=response_version, on_success_event_name=on_success_event_name)        

    def build_request(self, request_object:T, reference:Optional[str] = None, priority:Optional[int] = None) -> PublishEnvelope:        
        callback_payload = request_object.json()
        
        source_message_id = None
        group_trace_key = None        
        
        if CallbackContext.is_available():
            source_message_id = CallbackContext.message_id.get()
            group_trace_key = CallbackContext.group_trace_key.get()
            priority_raw = CallbackContext.priority.get()
            
            if priority == None and priority_raw != None:
                converted = int(priority_raw)
                priority = converted if converted > 0 else None 
        
        publish_request = ConcurrentCommandRequest().Create(
                command_name=self.command_name, command_reference=reference,
                content=callback_payload, process_wenhook_name=self.process_webhook_name,
                dispatcher=self.processor_name, application_name=self.application_name, priority=priority)
        
        if (source_message_id != None):
            publish_request.AddTracingData(source_message_id=source_message_id, group_trace_key=group_trace_key)     
        
        if (self.on_success_event_name != None and self.on_success_event_name != ''):
            publish_request.PublishEventOnSuccess(event_name=self.on_success_event_name, event_version=self.response_version)
            
        envelope = PublishEnvelope().Create(
            publish_request=publish_request,
            endpoint=self.publish_url,
            handler_name=self.processor_name,
            reference=reference,
            source_message_id=source_message_id,
            group_trace_key=group_trace_key,
            priority=priority
        )

        # Set DeDuplicate Details after building the base request using request.AddDeDuplicationInstruction()
       
        return envelope     

         
    

