from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Type
from orchestrator_sdk.seedworks.config_reader import ConfigReader
from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from orchestrator_sdk.seedworks.logger import Logger
from orchestrator_sdk.contracts.requests.commands.raise_command_request import RaiseCommandRequest
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope
from orchestrator_sdk.callback.processing_context import ProcessingContext

import hashlib
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
    de_duplication_delay_in_minutes: Optional[int] = None
    
    @staticmethod
    def hash_and_convert_to_string(content: Optional[str]) -> Optional[str]:
        if content is None:
            return None

        hash_object = hashlib.sha256()
        hash_object.update(content.encode())
        hash_hex = hash_object.hexdigest()  # Convert binary hash to hex string

        return hash_hex
   
    def __init__(self, processor_name:str, command_name:str, request_type:type, command_version:Optional[str] = None,
                 de_duplication_enabled:Optional[bool] = None, de_duplication_delay_in_minutes: Optional[int] = None) -> None:
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
        self.de_duplication_delay_in_minutes = de_duplication_delay_in_minutes
        
    def build_unique_header(self, request_object:T) -> Optional[str]:
        return None
   
    def build_request(self, request_object:T, processing_context:ProcessingContext, reference:Optional[str] = None, priority:Optional[int] = None) -> RaiseCommandRequest:        
        serialized_payload = request_object.json()
        
        unique_header_string = self.build_unique_header(request_object) 
        unique_header_hash = CommandRaiserBase.hash_and_convert_to_string(unique_header_string)    

        if (priority != None and (priority < 0 or priority > 1000)):
            raise Exception(f'Trying to set priority [{priority}], failed as it is not between 1 and 1000')

        publish_request = RaiseCommandRequest.Create(
                command_name=self.command_name, command_reference=reference,
                content=serialized_payload, application_name=self.application_name, 
                priority=priority, unique_request_header_hash=unique_header_hash)

        envelope = PublishEnvelope.Create(
            publish_request=publish_request,
            endpoint=self.publish_url,
            message_name=self.command_name,
            handler_name=self.processor_name,
            reference=reference,
            processing_context=processing_context,
            priority=priority,
            de_duplication_enabled=self.de_duplication_enabled,
            de_duplication_delay_in_seconds=self.de_duplication_delay_in_minutes,
            unique_header_hash=unique_header_hash)
        
        return envelope