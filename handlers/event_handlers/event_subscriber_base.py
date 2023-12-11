from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List
from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from seedworks.config_reader import ConfigReader
from seedworks.logger import Logger

import requests
import json

T = TypeVar('T')

logger = Logger.get_instance()

class EventSubscriberBase(ABC, Generic[T]):
    
    message_name:str = None
    processor_name:str = None
    process_webhook_name:str = None
    process_request_type:type = None
    application_name:str = None
    message_version:Optional[str] = None
 
   
    def __init__(self, processor_name:str, message_name:str, process_request_type, message_version:Optional[str] = None) -> None:
        super().__init__()
        
        ConfigReader.load()        
        orchestrator_settings = ConfigReader.section('orchestrator', OrchestratorConfig)
        
        print(process_request_type)
        
        self.process_request_type = process_request_type
        self.message_version = message_version
       
        self.process_locally = orchestrator_settings.process_locally
        self.process_webhook_name = orchestrator_settings.default_callback_webhook['name']
        self.application_name = orchestrator_settings.application_name
        
        self.processor_name = processor_name        
        self.message_name = message_name
        
    @abstractmethod
    async def _process(self, request: T, name:str, external_reference:Optional[str]) -> None:
        pass    
            
    async def process(self, request: T, message_name:str, external_reference:Optional[str]) -> None:
        if self.message_name.lower() != message_name.lower():
            raise ValueError(f'Trying to process message [{message_name}] in handler [{self.processor_name}] but it is not a supported.')
        return await self._process(request, message_name, external_reference)
    

