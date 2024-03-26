from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Type
from orchestrator_sdk.seedworks.config_reader import ConfigReader
from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from orchestrator_sdk.seedworks.logger import Logger
from orchestrator_sdk.contracts.requests.commands.raise_command_request import RaiseCommandRequest
from orchestrator_sdk.callback_context import CallbackContext
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope

logger = Logger.get_instance()

T = TypeVar('T')

class CommandRaiserBase(ABC, Generic[T]): 
    publish_path:str = '/Commands/RaiseCommand' 
    
    command_name:str
    request_type:type
    application_name:str
    publish_url:str
    processor_name:str     
    command_version:Optional[str] = None
    de_duplication_enabled:Optional[bool] = None
   
    def __init__(self, processor_name:str, command_name:str, request_type:type, command_version:Optional[str] = None, de_duplication_enabled:Optional[bool] = None) -> None:
        super().__init__()
        
        config_reader = ConfigReader()
        orchestrator_settings:OrchestratorConfig = config_reader.section('orchestrator', OrchestratorConfig)   
      
        self.publish_url = f'{orchestrator_settings.base_url}{self.publish_path}'        
        self.request_type =  request_type
        self.command_version = command_version
        self.application_name = orchestrator_settings.application_name        
        self.processor_name = processor_name
        self.command_name = command_name
        self.de_duplication_enabled = de_duplication_enabled
        
    def build_unique_header(self, request_object:T) -> Optional[str]:
        return None
   
    def build_request(self, request_object:T, reference:Optional[str] = None, priority:Optional[int] = None) -> RaiseCommandRequest:        
        serialized_payload = request_object.json()
        
        unique_header = self.build_unique_header(request_object)        
        
        source_message_trace_id = None        
        if CallbackContext.is_available():
            source_message_trace_id = CallbackContext.message_trace_id.get()
            
        publish_request = RaiseCommandRequest.Create(
                command_name=self.command_name, command_reference=reference,
                content=serialized_payload, application_name=self.application_name, 
                priority=priority, source_message_trace_id=source_message_trace_id, unique_request_header=unique_header)

        envelope = PublishEnvelope.Create(
            publish_request=publish_request,
            endpoint=self.publish_url,
            message_name=self.command_name,
            handler_name=self.processor_name,
            reference=reference,
            source_message_trace_id=source_message_trace_id,
            priority=priority,
            de_duplication_enabled=self.de_duplication_enabled,
            unique_header=unique_header
            )
        
        return envelope