from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Type
from orchestrator_sdk.seedworks.config_reader import ConfigReader
from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from orchestrator_sdk.seedworks.logger import Logger
from orchestrator_sdk.contracts.requests.events.publish_event_request import PublishEventRequest
from orchestrator_sdk.callback_context import CallbackContext
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope

logger = Logger.get_instance()

T = TypeVar('T')

class EventPublisherBase(ABC, Generic[T]):    
    event_name:str = None
    request_type:Type[T] = None
    request_version:Optional[str] = None
    application_name:str = None
    publish_url:str = None
    processor_name:str = None
    publish_path:str = '/Events/PublishEvent' 
 
   
    def __init__(self, processor_name:str, event_name:str, request_type:type, request_version:Optional[str] = None) -> None:
        super().__init__()
        
        config_reader = ConfigReader()
        orchestrator_settings:OrchestratorConfig = config_reader.section('orchestrator', OrchestratorConfig)   
      
        self.publish_url = f'{orchestrator_settings.base_url}{self.publish_path}'        
        self.request_type =  request_type
        self.request_version = request_version       
        self.application_name = orchestrator_settings.application_name        
        self.processor_name = processor_name
        self.event_name = event_name      
   
    def build_request(self, request_object:T, reference:Optional[str] = None, priority:Optional[int] = None) -> PublishEventRequest:        
        serialized_payload = request_object.json()
        
        source_message_id = None
        group_trace_key = None
        
        if CallbackContext.is_available():
            source_message_id = CallbackContext.message_id.get()
            group_trace_key = CallbackContext.group_trace_key.get()
            priority_raw = CallbackContext.priority.get()
            
            if priority == None and priority_raw != None:
                converted = int(priority_raw)
                priority = converted if converted > 0 else None   
        
        publish_request:PublishEventRequest = PublishEventRequest().Create(
            application_name=self.application_name, event_name=self.event_name, priority=priority, 
            event_version=self.request_version, event_reference=reference, content=serialized_payload)
        
        if (source_message_id != None):
            publish_request.AddTracingData(source_message_id=source_message_id, group_trace_key=group_trace_key)
            
        envelope = PublishEnvelope().Create(
            publish_request=publish_request,
            endpoint=self.publish_url,
            handler_name=self.processor_name,
            reference=reference,
            source_message_id=source_message_id,
            group_trace_key=group_trace_key,
            priority=priority)

        # Set DeDuplicate Details after building the base request using request.AddDeDuplicationInstruction()
        
        return envelope