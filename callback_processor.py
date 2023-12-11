from typing import Dict, List
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
        
    def _get_dispatcher_name(self, parms) -> str:
        if parms.get('DispatcherName') is not None:
            return parms['DispatcherName']        
        return None        
    
    def _get_external_reference(self, parms) -> str:
        if parms.get('ExternalReference') is not None:
            return parms['ExternalReference']        
        return None        
    
    def _get_action_type(self, parms) -> ActionType:
        string_action_type = parms['ActionType']
        converted:ActionType = ActionType[string_action_type]
        return converted
    
    def _get_message_type(self, parms):
        string_message_type = parms['MessageType']
        converted:MessageType = MessageType[string_message_type]
        return converted
    
    def _get_process_structure(self, parms) -> ProcessStructure:
        string_process_structure = parms['ProcessStructure']
        converted:ProcessStructure = ProcessStructure[string_process_structure]
        return converted
        
    def _get_message_name(self, parms) -> str:
        return parms['MessageName']
    
    
    async def _process_command(self, processor_name:str, external_reference:str, message_name:str, action_type:ActionType, json_payload:str):        
        handler = self.command_handlers[processor_name]
        
        if (action_type == ActionType.Process):
            request =  self.from_json(json_payload, handler.process_request_type)
            return await handler.process(request=request, message_name=message_name, external_reference=external_reference)            
        
        if (action_type == ActionType.OnSuccess):
            request =  self.from_json(json_payload, handler.on_success_class_type)          
            return await handler.on_success(request=request, message_name=message_name, external_reference=external_reference)
    
    async def _process_event(self, processor_name:str, external_reference:str, message_name:str, json_payload:str):        
        handler = self.event_handlers[processor_name]        
        request =  self.from_json(json_payload, handler.process_request_type)
        return await handler.process(request=request, message_name=message_name, external_reference=external_reference)    
    
        
    def process(self, json_payload, query_parms): 
        dispatcher_name:str = self._get_dispatcher_name(query_parms)
        action_type:ActionType = self._get_action_type(query_parms)
        external_reference:str = self._get_external_reference(query_parms)
        message_name:str = self._get_message_name(query_parms)
        process_structure:str = self._get_process_structure(query_parms)
        message_type:str = self._get_message_type(query_parms) 
        
        if (message_type == MessageType.Command):            
            return self._process_command(
                processor_name=dispatcher_name, external_reference=external_reference, 
                message_name=message_name, action_type=action_type, json_payload=json_payload
            )
        
        elif (message_type == MessageType.Event):
            return self._process_event(
                processor_name=dispatcher_name, external_reference=external_reference, 
                message_name=message_name, json_payload=json_payload
            )


     