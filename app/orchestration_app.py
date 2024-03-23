from orchestrator_sdk.app.sync_service import SyncService
from orchestrator_sdk.seedworks.config_reader import ConfigReader
from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from orchestrator_sdk.contracts.types.publish_adapter import PublishAdapter
from orchestrator_sdk.contracts.endpoints import Endpoints
from orchestrator_sdk.callback_processor import CallbackProcessor
from orchestrator_sdk.message_processors.commands.command_processor_base import CommandProcessorBase
from orchestrator_sdk.message_processors.commands.command_raiser_base import CommandRaiserBase
from orchestrator_sdk.message_processors.events.event_publisher_base import EventPublisherBase
from orchestrator_sdk.message_processors.events.event_subscriber_base import EventSubscriberBase
from orchestrator_sdk.data_access.message_broker.message_broker_publisher_interface import MessageBrokerPublisherInterface
from orchestrator_sdk.data_access.message_broker.publish_directly import PublishDirectly
from orchestrator_sdk.data_access.message_broker.publish_locally import PublishLocally
from orchestrator_sdk.data_access.message_broker.publish_outbox_with_2pc import PublishOutboxWith2PC
from orchestrator_sdk.data_access.database.unit_of_work import UnitOfWork
from orchestrator_sdk.data_access.database.services.local_outbox_service import LocalOutboxService
from typing import Optional

from orchestrator_sdk.data_access.database.database_context import DatabaseContext
from orchestrator_sdk.data_access.database.message_database import message_database

import asyncio

# @singleton
class OrchestrationApp():
    
    syncronized_with_orchestrator: bool = False
    application_name: str = None
    endpoints: Endpoints = None
    base_url: str = None
    default_callback_webhook: str = None    
  
    command_raisers: dict[str, CommandRaiserBase] = {}
    command_processors: dict[str, CommandProcessorBase] = {}
    
    event_subscribers: dict[str, EventSubscriberBase] = {}
    event_publishers: dict[str, EventPublisherBase] = {}    
    
    processor:CallbackProcessor = None
    publisher:MessageBrokerPublisherInterface = None  
    
    async def process_request(self, jsonPayload, unit_of_work:UnitOfWork):     
        return await self.processor.process(jsonPayload, unit_of_work)

    def add_command_raiser(self, command_raiser:CommandRaiserBase):
        self.command_raisers[command_raiser.processor_name] = command_raiser
        
    def add_command_processor(self, command_processor:CommandProcessorBase):
        self.command_processors[command_processor.processor_name] = command_processor        
        
    def add_event_subscriber(self, event_subscriber:EventSubscriberBase):
        self.event_subscribers[event_subscriber.processor_name] = event_subscriber
        
    def add_event_publisher(self, event_publisher:EventPublisherBase):
        self.event_publishers[event_publisher.processor_name] = event_publisher
    
    def __init__(self) -> bool:       
        
        self.processor = CallbackProcessor(
            command_raisers=self.command_raisers,
            command_processors=self.command_processors,
            event_publishers=self.event_publishers,
            event_subscribers=self.event_subscribers)
        
    def start(self, application_database:Optional[DatabaseContext] = None):        
        config_reader = ConfigReader()
        environment:str = config_reader.section('environment', str)     
        orchestrator_settings:OrchestratorConfig = config_reader.section('orchestrator', OrchestratorConfig)
        
        raw_adapter = orchestrator_settings.publish_adapter
        configured_adapter:PublishAdapter = None
        
        if raw_adapter in PublishAdapter.__members__:
            configured_adapter = PublishAdapter[raw_adapter]
        else:
            configured_adapter = PublishAdapter.Undefined
        
        adapter_selector = configured_adapter if configured_adapter != None and configured_adapter != PublishAdapter.Undefined else PublishAdapter.Direct
        
        if adapter_selector == PublishAdapter.Local:
            if environment != None and (environment.lower() != 'dev' or environment.lower() != 'development'):
                raise Exception(f'Unable to start the application, you are not allowed to use local processing in any environment than development. [{environment}]')                
            self.publisher = PublishLocally()        
        elif adapter_selector == PublishAdapter.Direct:
            self.publisher = PublishDirectly()
        elif adapter_selector == PublishAdapter.OutboxWith2PC:
            self.publisher = PublishOutboxWith2PC()
        else:
            raise Exception(f"You have configured an unsupported publisher adapter type [{adapter_selector.name}] please select an valid adapter (Direct, Outbox).")
        
        message_database.init()
        
        if (application_database != None):
            application_database.init()
      
        self.application_name = orchestrator_settings.application_name
        self.processor.application_name = self.application_name        
        self.endpoints = Endpoints(orchestrator_settings.base_url)
        
        subscribers = self.event_subscribers.values()
        publishers = self.event_publishers.values()
        raisers = self.command_raisers.values()
        processors = self.command_processors.values()
        
        sync_service = SyncService() 
        self.syncronized_with_orchestrator = sync_service.init(settings=orchestrator_settings, endpoints=self.endpoints, 
           event_publishers=publishers, event_subscribers=subscribers, command_raisers=raisers, command_processors=processors)
        
        outbox_service = LocalOutboxService(message_database)
        asyncio.create_task(outbox_service.check_for_messages_that_are_ready())
        
orchestration_app = OrchestrationApp()

