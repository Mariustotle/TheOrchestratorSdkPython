from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Type
from seedworks.config_reader import ConfigReader
from seedworks.logger import Logger

from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from orchestrator_sdk.contracts.requests.events.publish_event_request import PublishEventRequest
from orchestrator_sdk.data_access.orchestrator_publisher import OrchestratorPublisher
from orchestrator_sdk.callback_context import CallbackContext

T = TypeVar('T')

logger = Logger.get_instance()

class EventPublisherBase(ABC, Generic[T]):    
    event_name:str = None
    request_type:type = None
    request_version:Optional[str] = None
    application_name:str = None
    publisher:OrchestratorPublisher = None
    publish_url:str = None
    processor_name:str = None
        
    publish_path:str = '/Events/PublishEvent' 
 
   
    def __init__(self, processor_name:str, event_name:str, request_version:Optional[str] = None) -> None:
        super().__init__()
        
        ConfigReader.load()
        orchestrator_settings = ConfigReader.section('orchestrator', OrchestratorConfig)
        
        self.publish_url = f'{orchestrator_settings.base_url}{self.publish_path}'
        
        self.request_type = Type[T]
        self.request_version = request_version
       
        self.process_locally = orchestrator_settings.process_locally
        self.application_name = orchestrator_settings.application_name
        
        self.processor_name = processor_name
        self.event_name = event_name
        
        self.publisher = OrchestratorPublisher()
   
    def build_request(self, request_object:T, reference:Optional[str] = None) -> PublishEventRequest:        
        serialized_payload = request_object.json()
        
        source_message_id = None
        group_trace_id = None
        if CallbackContext.is_available():
            source_message_id = CallbackContext.message_id.get()
            group_trace_id = CallbackContext.group_trace_key.get()
        
        request:PublishEventRequest = PublishEventRequest().Create(
            application_name=self.application_name, event_name=self.event_name, event_version=self.request_version, 
            event_reference=reference, content=serialized_payload)
        
        if (source_message_id != None):
            request.AddTracingData(source_message_id=source_message_id, group_trace_key=group_trace_id)     

        # Set DeDuplicate Details after building the base request using request.AddDeDuplicationInstruction()
        
        return request     

    async def publish(self, request:PublishEventRequest, reference:str) -> None:
                    
        if (self.process_locally): 
            # Try sending to Orchestrator and fallbck to a SQLite outbox pattern
            pass
            
        else:
            await self.publisher.post(request=request, url=self.publish_url, description=f'Event publisher for {self.event_name}', reference=reference)           