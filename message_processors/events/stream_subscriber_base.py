from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional
from orchestrator_sdk.seedworks.logger import Logger

from orchestrator_sdk.callback.processing_context import ProcessingContext
from orchestrator_sdk.seedworks.config_reader import ConfigReader
from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from orchestrator_sdk.data_access.database.unit_of_work import UnitOfWork

T = TypeVar('T')

logger = Logger.get_instance()

class StreamSubscriberBase(ABC, Generic[T]):
    
    event_name:str
    processor_name:str
    process_webhook_name:str
    request_type:type
    application_name:str    
    event_version:Optional[str] = None    
   
    def __init__(self, processor_name:str, event_name:str, request_type:type, 
            event_version:Optional[str] = None) -> None:
        
        super().__init__()       
        
        config_reader = ConfigReader()
        orchestrator_settings:OrchestratorConfig = config_reader.section('orchestrator', OrchestratorConfig)   
      
        self.request_type = request_type
        self.event_version = event_version
        self.event_name = event_name

        self.process_webhook_name = orchestrator_settings.default_callback_webhook.name
        self.application_name = orchestrator_settings.application_name
        
        self.processor_name = processor_name
        
        
    @abstractmethod
    async def _process(self, request: T, name:str, processing_context: ProcessingContext, reference:Optional[str], unit_of_work:Optional[UnitOfWork] = None) -> None:
        pass    
            
    async def process(self, request: T, event_name:str, processing_context: ProcessingContext, reference:Optional[str], unit_of_work:Optional[UnitOfWork] = None) -> None:
        if self.event_name.lower() != event_name.lower():
            raise ValueError(f'Trying to process event [{event_name}] in handler [{self.processor_name}] but it is not a supported.')
        
        try:
            return await self._process(request, event_name, processing_context, reference, unit_of_work)
        
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")  
            raise # re-throw after writing error to screen
        
        
        
    

