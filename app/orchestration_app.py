from orchestrator_sdk.app.sync_service import SyncService
from orchestrator_sdk.seedworks.config_reader import ConfigReader
from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from orchestrator_sdk.contracts.endpoints import Endpoints
from orchestrator_sdk.callback.processors.command_processor import CommandProcessor
from orchestrator_sdk.callback.processors.event_processor import EventProcessor
from orchestrator_sdk.callback.processors.stream_processor import StreamProcessor

from orchestrator_sdk.message_processors.commands.command_processor_base import CommandProcessorBase
from orchestrator_sdk.message_processors.commands.command_raiser_base import CommandRaiserBase
from orchestrator_sdk.message_processors.events.event_publisher_base import EventPublisherBase
from orchestrator_sdk.message_processors.events.event_subscriber_base import EventSubscriberBase
from orchestrator_sdk.message_processors.StreamOutbound.stream_subscriber_base import StreamSubscriberBase
from orchestrator_sdk.data_access.message_broker.outbox_publisher import OutboxPublisher
from typing import Optional

from orchestrator_sdk.data_access.database.database_context import DatabaseContext
from orchestrator_sdk.data_access.database.message_database import message_database

from orchestrator_sdk.seedworks.logger import Logger
logger = Logger.get_instance()

class OrchestrationApp():
    
    syncronized_with_orchestrator: bool = False
    application_name: str = None
    endpoints: Endpoints = None
    base_url: str = None
    default_callback_webhook: str = None
    orchestrator_settings:OrchestratorConfig = None
  
    command_raisers: dict[str, CommandRaiserBase] = {}
    command_processors: dict[str, CommandProcessorBase] = {}
    
    event_subscribers: dict[str, EventSubscriberBase] = {}
    event_publishers: dict[str, EventPublisherBase] = {}    

    stream_subscribers: dict[str, StreamSubscriberBase] = {}    
    
    command_processor:CommandProcessor = None
    event_processor:EventProcessor = None
    stream_processor:StreamProcessor = None

    publisher:OutboxPublisher = None  

    def add_command_raiser(self, command_raiser:CommandRaiserBase):
        self.command_raisers[command_raiser.processor_name] = command_raiser
        
    def add_command_processor(self, command_processor:CommandProcessorBase):
        self.command_processors[command_processor.processor_name] = command_processor        
        
    def add_event_subscriber(self, event_subscriber:EventSubscriberBase):
        self.event_subscribers[event_subscriber.processor_name] = event_subscriber
        
    def add_event_publisher(self, event_publisher:EventPublisherBase):
        self.event_publishers[event_publisher.processor_name] = event_publisher

    def add_stream_subscriber(self, stream_subscriber:StreamSubscriberBase):
        self.stream_subscribers[stream_subscriber.processor_name] = stream_subscriber

    
    def __init__(self) -> bool:

        config_reader = ConfigReader()
        environment:str = config_reader.section('environment', str)     
        self.orchestrator_settings = config_reader.section('orchestrator', OrchestratorConfig)
        self.application_name = self.orchestrator_settings.application_name
        self.base_url = self.orchestrator_settings.base_url
        
        self.command_processor = CommandProcessor(application_name=self.application_name, command_raisers=self.command_raisers, command_processors=self.command_processors)
        self.event_processor = EventProcessor(application_name=self.application_name, event_publishers=self.event_publishers, event_subscribers=self.event_subscribers)
        self.stream_processor = StreamProcessor(application_name=self.application_name, stream_subscribers=self.stream_subscribers)
        
        self.publisher = OutboxPublisher()
        
    def start(self, application_database:Optional[DatabaseContext] = None):        
        message_database.init()
        
        if (application_database != None):
            application_database.init()      
       
        self.endpoints = Endpoints(self.base_url)
        
        subscribers = self.event_subscribers.values()
        publishers = self.event_publishers.values()
        raisers = self.command_raisers.values()
        processors = self.command_processors.values()
        stream_subscribers = self.stream_subscribers.values()
        
        sync_service = SyncService() 
        self.syncronized_with_orchestrator = sync_service.init(settings=self.orchestrator_settings, endpoints=self.endpoints, 
           event_publishers=publishers, event_subscribers=subscribers, command_raisers=raisers, command_processors=processors, stream_subscribers=stream_subscribers)
        
        if (self.orchestrator_settings.use_simulator):
            logger.warning('The Orchestrator client is currently run in SIMULATOR mode only intended for local testing.')
        
orchestration_app = OrchestrationApp()

