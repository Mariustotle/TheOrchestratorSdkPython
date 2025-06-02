from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional
from orchestrator_sdk.seedworks.logger import Logger
from orchestrator_sdk.contracts.types.processing_type import ProcessingType
from orchestrator_sdk.callback.processing_context import ProcessingContext

from orchestrator_sdk.seedworks.config_reader import ConfigReader
from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from orchestrator_sdk.data_access.database.unit_of_work import UnitOfWork

T = TypeVar('T')

logger = Logger.get_instance()

class CommandProcessorBase(ABC, Generic[T]):
    
    command_name:str
    processor_name:str
    process_webhook_name:str
    request_type:type
    processing_type:ProcessingType
    
    application_name: str = None
    latest_version: Optional[str] = None
    de_duplication_enabled: Optional[bool] = None
    de_duplication_delay_in_minutes: Optional[int] = None
    max_concurrency_limit: Optional[int] = None
    requires_command_raiser_approval: Optional[int] = None
   
    def __init__(self, processor_name:str, command_name:str, request_type:type, process_type:Optional[ProcessingType] = ProcessingType.Concurrent, 
                 de_duplication_enabled:Optional[bool] = None, max_concurrency_limit:Optional[int] = None, requires_command_raiser_approval:Optional[bool] = None,
                 latest_version:Optional[str] = None, de_duplication_delay_in_minutes: Optional[int] = None) -> None:
        super().__init__()       
        
        config_reader = ConfigReader()
        orchestrator_settings:OrchestratorConfig = config_reader.section('orchestrator', OrchestratorConfig)   
      
        self.request_type = request_type
        self.latest_version = latest_version
        self.command_name = command_name
        self.process_webhook_name = orchestrator_settings.default_callback_webhook.name
        self.application_name = orchestrator_settings.application_name        
        self.processor_name = processor_name
        self.processing_type = process_type
        self.de_duplication_enabled = de_duplication_enabled
        self.de_duplication_delay_in_minutes = de_duplication_delay_in_minutes
        self.max_concurrency_limit = max_concurrency_limit
        self.requires_command_raiser_approval = requires_command_raiser_approval
        
    @abstractmethod
    async def _process(self, request: T, context: ProcessingContext, unit_of_work:Optional[UnitOfWork] = None) -> None:
        pass    
            
    async def process(self, request: T, processing_context: ProcessingContext, unit_of_work:Optional[UnitOfWork] = None) -> None:
        if self.command_name.lower() != processing_context.message_name.lower():
            raise ValueError(f'Trying to process command [{processing_context.message_name}] in handler [{self.processor_name}] but it is not a supported.')        
        
        try:
            return await self._process(request=request, context=processing_context, unit_of_work=unit_of_work)
        
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")  
            raise # re-throw after writing error to screen
            
        
        
        
        
    

