from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List
from sdk.contracts.orchestrator_config import OrchestratorConfig
from seedworks.config_reader import ConfigReader
from seedworks.logger import Logger
from sdk.contracts.requests.events.publish_event_request import PublishEventRequest
from sdk.data_access.orchestrator_publisher import OrchestratorPublisher

T = TypeVar('T')

logger = Logger.get_instance()

class EventPublisherBase(ABC, Generic[T]):
    
    message_name:str = None
    payload_type:type = None
    application_name:str = None
    message_version:Optional[str] = None
    publisher:OrchestratorPublisher = None
    publish_url:str = None
    processor_name:str = None
        
    publish_path:str = '/Events/PublishEvent' 
 
   
    def __init__(self, processor_name:str, message_name:str, payload_type, message_version:Optional[str] = None) -> None:
        super().__init__()
        
        ConfigReader.load()
        orchestrator_settings = ConfigReader.section('orchestrator', OrchestratorConfig)
        
        self.publish_url = f'{orchestrator_settings.base_url}{self.publish_path}'
        
        self.payload_type = payload_type
        self.message_version = message_version
       
        self.process_locally = orchestrator_settings.process_locally
        self.application_name = orchestrator_settings.application_name
        
        self.processor_name = processor_name
        self.message_name = message_name
        
        self.publisher = OrchestratorPublisher()
   
    def build_request(self, event_name:str, payload:T, client_reference:Optional[str] = None) -> PublishEventRequest:     
        
        serialized_payload = payload.json()     
        
        request = PublishEventRequest().Create(
            application_name=self.application_name, event_name=event_name, event_version=self.message_version, 
            event_reference=client_reference, content=serialized_payload)
        
        return request     

    async def publish(self, external_reference:str, request:PublishEventRequest) -> None:
                    
        if (self.process_locally): 
            # Try sending to Orchestrator and fallbck to a SQLite outbox pattern
            pass
            
        else:
            await self.publisher.post(request=request, url=self.publish_url, description=f'Event publisher for {self.message_name}', external_reference=external_reference)           