from orchestrator_sdk.app.sync_service import SyncService
from seedworks.config_reader import ConfigReader
from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from orchestrator_sdk.contracts.endpoints import Endpoints
from orchestrator_sdk.callback_processor import CallbackProcessor
from typing import Dict
from orchestrator_sdk.handlers.command_handlers.concurrent_command_handler_base import CommandHandlerBase
from orchestrator_sdk.handlers.event_handlers.event_subscriber_base import EventSubscriberBase
from orchestrator_sdk.handlers.event_handlers.event_publisher_base import EventPublisherBase

# @singleton
class OrchestrationApp():
    
    syncronized_with_orchestrator: bool = False
    application_name: str = None
    endpoints: Endpoints = None
    
    command_handlers: dict[str, CommandHandlerBase] = {}
    event_handlers: dict[str, EventSubscriberBase] = {}
    event_publishers: dict[str, EventPublisherBase] = {}    
    
    processor:CallbackProcessor = None
    
    async def process_request(self, jsonPayload, query_parms):     
        return await self.processor.process(jsonPayload, query_parms)
    
    def add_command_handler(self, handler:CommandHandlerBase):
        self.command_handlers[handler.processor_name] = handler
        
    def add_event_handler(self, handler:EventSubscriberBase):
        self.event_handlers[handler.processor_name] = handler
        
    def add_event_publisher(self, publisher:EventPublisherBase):
        self.event_publishers[publisher.processor_name] = publisher
    
    def __init__(self) -> bool:        
        self.processor = CallbackProcessor(command_handlers=self.command_handlers, 
                                           event_handlers=self.event_handlers, 
                                           event_publishers=self.event_publishers)
        
    def start(self):        
        ConfigReader.load()        
        orchestrator_settings = ConfigReader.section('orchestrator', OrchestratorConfig)
        
        self.application_name = orchestrator_settings.application_name
        self.endpoints = Endpoints(orchestrator_settings.base_url)
        
        subscriptions = self.event_handlers.values()
        publishers = self.event_publishers.values()
        
        sync_service = SyncService() 
        self.syncronized_with_orchestrator = sync_service.init(orchestrator_settings, self.endpoints, subscriptions, publishers)
        
orchestration_app = OrchestrationApp()

