from pydantic import UUID4
from typing import Dict, List

from orchestrator_sdk.callback_context import CallbackContext
from orchestrator_sdk.handlers.command_handlers.concurrent_command_handler_base import CommandHandlerBase
from orchestrator_sdk.handlers.event_handlers.event_subscriber_base import EventSubscriberBase
from orchestrator_sdk.handlers.event_handlers.event_publisher_base import EventPublisherBase

from orchestrator_sdk.contracts.types.action_type import ActionType
from orchestrator_sdk.contracts.types.message_type import MessageType
from orchestrator_sdk.contracts.types.process_structure import ProcessStructure

class CallbackProcessor:
    
    command_handlers: dict[str, CommandHandlerBase] = {} 
    event_handlers: dict[str, EventSubscriberBase] = {}
    event_publishers: dict[str, EventPublisherBase] = {}   

    def from_json(self, json_payload, class_type):
        
        if isinstance(json_payload, str):
            return class_type.parse_raw(json_payload)
        
        elif isinstance(json_payload, (dict, list)):
            return  class_type.parse_obj(json_payload)
        else:
            raise TypeError("json_data must be a JSON document in str, bytes, bytearray, dict, or list format")        
        
    def __init__(self, command_handlers, event_handlers, event_publishers): 
        self.command_handlers = command_handlers
        self.event_handlers = event_handlers
        self.event_publishers = event_publishers     
   
    async def _process_command(self, processor_name:str, reference:str, message_name:str, action_type:ActionType, json_payload:str):        
        handler = self.command_handlers[processor_name]
        
        if (action_type == ActionType.Process):
            request =  self.from_json(json_payload, handler.process_request_type)
            return await handler.process(request=request, message_name=message_name, reference=reference)            
        
        if (action_type == ActionType.OnSuccess):
            request =  self.from_json(json_payload, handler.on_success_class_type)          
            return await handler.on_success(request=request, message_name=message_name, reference=reference)
    
    async def _process_event(self, processor_name:str, reference:str, message_name:str, json_payload:str):        
        handler = self.event_handlers[processor_name]        
        request =  self.from_json(json_payload, handler.process_request_type)
        return await handler.process(request=request, message_name=message_name, reference=reference)    
    
        
    def process(self, json_payload):
        
        accountId:UUID4 = CallbackContext.account_id.get()
        group_trace_key:UUID4 = CallbackContext.group_trace_key.get()
        message_id:UUID4 = CallbackContext.message_id.get()  
        action_type:ActionType = CallbackContext.action_type.get()
        dispatcher:str = CallbackContext.dispatcher.get()
        reference:str = CallbackContext.reference.get()
        message_name:str = CallbackContext.message_name.get()
        message_type:str = CallbackContext.message_type.get()
        
        if (message_type == MessageType.Command):            
            return self._process_command(
                processor_name=dispatcher, reference=reference, 
                message_name=message_name, action_type=action_type, json_payload=json_payload
            )
        
        elif (message_type == MessageType.Event):
            return self._process_event(
                processor_name=dispatcher, reference=reference, 
                message_name=message_name, json_payload=json_payload
            )


     