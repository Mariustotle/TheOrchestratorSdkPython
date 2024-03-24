from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Type
from orchestrator_sdk.seedworks.config_reader import ConfigReader
from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from orchestrator_sdk.seedworks.logger import Logger
from orchestrator_sdk.contracts.requests.events.publish_event_request import PublishEventRequest
from orchestrator_sdk.callback_context import CallbackContext
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope
from orchestrator_sdk.contracts.types.processing_type import ProcessingType

logger = Logger.get_instance()

T = TypeVar('T')

class EventPublisherBase(ABC, Generic[T]):  
    publish_path:str = '/Events/PublishEvent' 
      
    event_name:str
    request_type:type   
    application_name:str
    publish_url:str
    processor_name:str
    processing_type:ProcessingType    
    
    latest_version:Optional[str] = None
    de_duplication_enabled:Optional[bool] = None
    allow_publishing_without_subscribers:Optional[bool] = None
    require_new_subscriber_approval:Optional[bool] = None
   
    def __init__(self, processor_name:str, event_name:str, request_type:type, latest_version:Optional[str] = None,
                 de_duplication_enabled:Optional[bool] = None, allow_publishing_without_subscribers:Optional[bool] = None,
                 processing_type:Optional[ProcessingType] = ProcessingType.Concurrent,
                 require_new_subscriber_approval:Optional[bool] = None) -> None:
        super().__init__()
        
        config_reader = ConfigReader()
        orchestrator_settings:OrchestratorConfig = config_reader.section('orchestrator', OrchestratorConfig)   
      
        self.publish_url = f'{orchestrator_settings.base_url}{self.publish_path}'        
        self.request_type =  request_type
        self.latest_version = latest_version       
        self.application_name = orchestrator_settings.application_name        
        self.processor_name = processor_name
        self.event_name = event_name
        self.processing_type = processing_type
        self.de_duplication_enabled = de_duplication_enabled
        self.allow_publishing_without_subscribers = allow_publishing_without_subscribers
        self.require_new_subscriber_approval = require_new_subscriber_approval
   
    def build_request(self, request_object:T, reference:Optional[str] = None, priority:Optional[int] = None) -> PublishEventRequest:        
        serialized_payload = request_object.json()
        
        source_trace_message_id = None
        
        if CallbackContext.is_available():
            source_trace_message_id = CallbackContext.trace_message_id.get()
        
        publish_request:PublishEventRequest = PublishEventRequest.Create(
            application_name=self.application_name, event_name=self.event_name, priority=priority,
            event_version=self.latest_version, event_reference=reference, content=serialized_payload, source_trace_message_id=source_trace_message_id)
            
        envelope = PublishEnvelope.Create(
            publish_request=publish_request,
            endpoint=self.publish_url,
            handler_name=self.processor_name,
            reference=reference,
            source_trace_message_id=source_trace_message_id,
            priority=priority)

        # Set DeDuplicate Details after building the base request using request.AddDeDuplicationInstruction()
        
        return envelope