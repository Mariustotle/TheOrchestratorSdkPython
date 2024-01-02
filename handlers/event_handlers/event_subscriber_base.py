from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Type
from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from seedworks.config_reader import ConfigReader
from seedworks.logger import Logger

T = TypeVar('T')

logger = Logger.get_instance()

class EventSubscriberBase(ABC, Generic[T]):
    
    event_name:str = None
    processor_name:str = None
    process_webhook_name:str = None
    request_type:type = None
    application_name:str = None
    request_version:Optional[str] = None
 
   
    def __init__(self, processor_name:str, event_name:str, request_type:type, request_version:Optional[str] = None) -> None:
        super().__init__()
        
        ConfigReader.load()        
        orchestrator_settings = ConfigReader.section('orchestrator', OrchestratorConfig)
        
        self.request_type = request_type
        self.request_version = request_version
        self.event_name = event_name
       
        self.process_locally = orchestrator_settings.process_locally
        self.process_webhook_name = orchestrator_settings.default_callback_webhook['name']
        self.application_name = orchestrator_settings.application_name
        
        self.processor_name = processor_name        
        
    @abstractmethod
    async def _process(self, request: T, name:str, reference:Optional[str]) -> None:
        pass    
            
    async def process(self, request: T, event_name:str, reference:Optional[str]) -> None:
        if self.event_name.lower() != event_name.lower():
            raise ValueError(f'Trying to process message [{event_name}] in handler [{self.processor_name}] but it is not a supported.')
        return await self._process(request, event_name, reference)
    

