from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional
from orchestrator_sdk.seedworks.logger import Logger
from orchestrator_sdk.seedworks.config_reader import ConfigReader
from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope
from orchestrator_sdk.data_access.local_persistance.unit_of_work import UnitOfWork

logger = Logger.get_instance()

T = TypeVar('T')
Y = TypeVar('Y')

class CommandHandlerBase(ABC, Generic[T, Y]):
    
    command_name:str = None
    processor_name:str = None
    process_webhook_name:str = None
    
    publish_url:str = None
    request_type:type = None
    request_version:Optional[str] = None
    response_type:type = None
    response_version:Optional[str] = None
    
    on_success_event_name:Optional[str]
    application_name:str = None

    
    def __init__(self,
            processor_name:str, 
            command_name:str, 
            publish_path:str,
            request_type:type,
            response_type:type,
            request_version:Optional[str] = None, 
            response_version:Optional[str] = None,
            on_success_event_name:Optional[str] = None 
            
            ) -> None:
        
        super().__init__()
        
        config_reader = ConfigReader()
        orchestrator_settings:OrchestratorConfig = config_reader.section('orchestrator', OrchestratorConfig)          
       
        self.request_type = request_type
        self.response_type = response_type      
        self.publish_url = f'{orchestrator_settings.base_url}{publish_path}'
        self.process_webhook_name = orchestrator_settings.default_callback_webhook.name
        self.application_name = orchestrator_settings.application_name        
        self.processor_name = processor_name
        self.request_version = request_version
        self.response_version = response_version        
        self.on_success_event_name = on_success_event_name        
        
        self.command_name = command_name
        
    @abstractmethod
    def build_request(self, request_object:T, reference:Optional[str] = None) -> PublishEnvelope:
        pass
    
    @abstractmethod
    async def _process(self, request: T, command_name:str, reference:Optional[str], unit_of_work:Optional[UnitOfWork] = None) -> Y:
        pass    
               
    async def process(self, request: T, command_name:str, reference:Optional[str], unit_of_work:Optional[UnitOfWork] = None) -> Y:
        if self.command_name.lower() != command_name.lower():
            raise ValueError(f'Trying to process message [{command_name}] in handler [{self.processor_name}] but it is not a supported.')
        
        response = await self._process(request, command_name, reference, unit_of_work)        
        return response