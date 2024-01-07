from orchestrator_sdk.app.sync_service import SyncService
from orchestrator_sdk.seedworks.config_reader import ConfigReader
from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from orchestrator_sdk.contracts.types.publish_adapter import PublishAdapter
from orchestrator_sdk.contracts.endpoints import Endpoints
from orchestrator_sdk.callback_processor import CallbackProcessor
from orchestrator_sdk.handlers.command_handlers.concurrent_command_handler_base import CommandHandlerBase
from orchestrator_sdk.handlers.event_handlers.event_subscriber_base import EventSubscriberBase
from orchestrator_sdk.handlers.event_handlers.event_publisher_base import EventPublisherBase
from orchestrator_sdk.data_access.message_broker.message_broker_publisher_interface import MessageBrokerPublisherInterface
from orchestrator_sdk.data_access.message_broker.publish_directly import PublishDirectly
from orchestrator_sdk.data_access.message_broker.publish_locally import PublishLocally
from orchestrator_sdk.data_access.message_broker.publish_outbox_with_2pc import PublishOutboxWith2PC
from orchestrator_sdk.data_access.local_persistance.unit_of_work import UnitOfWork

from orchestrator_sdk.data_access.local_persistance.local_database import local_database

# @singleton
class OrchestrationApp():
    
    syncronized_with_orchestrator: bool = False
    application_name: str = None
    endpoints: Endpoints = None
    base_url: str = None
    default_callback_webhook: str = None    
    
    command_handlers: dict[str, CommandHandlerBase] = {}
    event_handlers: dict[str, EventSubscriberBase] = {}
    event_publishers: dict[str, EventPublisherBase] = {}    
    
    processor:CallbackProcessor = None
    publisher:MessageBrokerPublisherInterface = None  
    
    async def process_request(self, jsonPayload, unit_of_work:UnitOfWork):     
        return await self.processor.process(jsonPayload, unit_of_work)

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
        
        local_database.init()
      
        self.application_name = orchestrator_settings.application_name
        self.processor.application_name = self.application_name        
        self.endpoints = Endpoints(orchestrator_settings.base_url)
        
        subscriptions = self.event_handlers.values()
        publishers = self.event_publishers.values()
        
        sync_service = SyncService() 
        self.syncronized_with_orchestrator = sync_service.init(orchestrator_settings, self.endpoints, subscriptions, publishers)
        
orchestration_app = OrchestrationApp()

