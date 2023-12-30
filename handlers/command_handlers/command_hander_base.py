from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List
from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from orchestrator_sdk.data_access.orchestrator_publisher import OrchestratorPublisher
from seedworks.config_reader import ConfigReader
from seedworks.logger import Logger

T = TypeVar('T')
Y = TypeVar('Y')

logger = Logger.get_instance()

class CommandHandlerBase(ABC, Generic[T, Y]):
    
    message_name:str = None
    processor_name:str = None
    process_webhook_name:str = None
    on_success_webhook_name:Optional[str] = None
    publish_url:str = None
    process_request_type:type = None
    on_success_class_type:type = None
    application_name:str = None
    publisher:OrchestratorPublisher = None
    
    def __init__(self, processor_name:str, message_name:str, process_request_type, on_success_class_type, publish_path,
                 use_success_webhook:bool = False) -> None:
        super().__init__()
        
        ConfigReader.load()        
        orchestrator_settings = ConfigReader.section('orchestrator', OrchestratorConfig)
        
        self.process_request_type = process_request_type
        self.on_success_class_type = on_success_class_type
        
        self.process_locally = orchestrator_settings.process_locally
        self.publish_url = f'{orchestrator_settings.base_url}{publish_path}'
        self.process_webhook_name = orchestrator_settings.default_callback_webhook['name']
        self.application_name = orchestrator_settings.application_name
        
        self.processor_name = processor_name        
        self.on_success_webhook_name = orchestrator_settings.default_callback_webhook['name'] if use_success_webhook else None
        
        self.message_name = message_name
        self.publisher = OrchestratorPublisher()
        
    @abstractmethod
    def build_request(self, request_object:T, reference:Optional[str] = None):
        pass
    
    @abstractmethod
    async def _process(self, request: T, name:str, reference:Optional[str]) -> Y:
        pass
    
    @abstractmethod
    async def _on_success(self, request: Y, name:str, reference:Optional[str]):
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

    async def on_success(self, request: T, message_name:str, reference:Optional[str]):
        if self.message_name.lower() != message_name.lower():
            raise ValueError(f'Trying to complete message [{message_name}] in handler [{self.processor_name}] but it is not a supported message.') 
        
        response = await self._on_success(request, message_name, reference)        
        return response