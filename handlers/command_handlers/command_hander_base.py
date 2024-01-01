from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Type
from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from orchestrator_sdk.data_access.orchestrator_publisher import OrchestratorPublisher
from seedworks.config_reader import ConfigReader
from seedworks.logger import Logger

T = TypeVar('T')
Y = TypeVar('Y')

logger = Logger.get_instance()

class CommandHandlerBase(ABC, Generic[T, Y]):
    
    command_name:str = None
    processor_name:str = None
    process_webhook_name:str = None

    publish_url:str = None
    request_type:type = None
    request_version:Optional[str] = None
    response_type:type = None
    response_version:Optional[str] = None
    process_response_type:type = None
    
    on_success_event_name:Optional[str]
    application_name:str = None
    publisher:OrchestratorPublisher = None
    
    def __init__(self,
            processor_name:str, 
            command_name:str, 
            publish_path:str,
            request_version:Optional[str] = None, 
            response_version:Optional[str] = None,
            on_success_event_name:Optional[str] = None          
            ) -> None:
        
        super().__init__()
                
        ConfigReader.load()        
        orchestrator_settings = ConfigReader.section('orchestrator', OrchestratorConfig)
        
        self.request_type = Type[T]
        self.response_type = Type[Y]
        
        self.process_locally = orchestrator_settings.process_locally
        self.publish_url = f'{orchestrator_settings.base_url}{publish_path}'
        self.process_webhook_name = orchestrator_settings.default_callback_webhook['name']
        self.application_name = orchestrator_settings.application_name        
        self.processor_name = processor_name
        self.request_version = request_version
        self.response_version = response_version
        
        if (on_success_event_name != None and on_success_event_name != ''):
            self.on_success_event_name = on_success_event_name
        
        self.command_name = command_name
        self.publisher = OrchestratorPublisher()
        
    @abstractmethod
    def build_request(self, request_object:T, reference:Optional[str] = None):
        pass
    
    @abstractmethod
    async def _process(self, request: T, name:str, reference:Optional[str]) -> Y:
        pass    
   
    async def publish(self, request, reference:Optional[str] = None):
                    
        if (self.process_locally): 
            # Need to inflate the payload as well
            # inflated = self.from_json(request.RequestPayload, self.process_request_type)
            response = await self.process(request, message_name=request.CommandName, reference=reference)
            await self.on_success(request=response, message_name=request.CommandName, reference=reference)
            
            return response
            
        else:
            response = await self.publisher.post(request, self.publish_url, f'Command Publisher for {self.processor_name}', reference=reference)                        
            return response
            
    async def process(self, request: T, message_name:str, reference:Optional[str]) -> Y:
        if self.message_name.lower() != message_name.lower():
            raise ValueError(f'Trying to process message [{message_name}] in handler [{self.processor_name}] but it is not a supported.')
        
        response = await self._process(request, message_name, reference)        
        return response