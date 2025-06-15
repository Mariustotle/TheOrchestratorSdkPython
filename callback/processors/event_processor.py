from orchestrator_sdk.callback.processors.processor_base import ProcessorBase
from orchestrator_sdk.data_access.database.unit_of_work import UnitOfWork
from orchestrator_sdk.callback.callback_types.event_callback import EventCallback, EventHeaders
from orchestrator_sdk.callback.processing_context import ProcessingContext
from orchestrator_sdk.message_processors.events.event_subscriber_base import EventSubscriberBase
from orchestrator_sdk.message_processors.events.event_publisher_base import EventPublisherBase
from orchestrator_sdk.callback.header_properties import HeaderProperties
from orchestrator_sdk.contracts.types.activity_type import ActivityTypeEnum

class EventProcessor(ProcessorBase):
    
    callback_headers: EventHeaders = None
    event_publishers: dict[str, EventPublisherBase] = {} 
    event_subscribers: dict[str, EventSubscriberBase] = {} 
    
    def __init__(self, application_name:str, event_publishers, event_subscribers): 
        self.event_publishers = event_publishers
        self.event_subscribers = event_subscribers

        ProcessorBase.__init__(self, application_name)

    def get_header_properties(self, headers:HeaderProperties) -> EventHeaders:
        return EventHeaders.Create(
            message_trace_id_string=headers.trace_message_id,
            message_id_string=headers.message_id,
            message_name=headers.message_name,
            application_name=headers.application_name,
            dispatcher=headers.dispatcher,
            activity_type_string=headers.activity_type,
            message_type_string=headers.message_type,
            reference=headers.reference,
            priority_string=headers.priority
        )
    
    def get_processing_context(self, headers:EventHeaders) -> ProcessingContext: 
        return ProcessingContext.Create(source_message_trace_id= headers.message_trace_id, source_priority=headers.priority, message_name=headers.message_name, reference=headers.reference)

    async def process_specific(self, json_content, callback: EventCallback, headers:EventHeaders, processing_context:ProcessingContext, unit_of_work:UnitOfWork) -> object:
        response_object = None

        if (headers.activity_type != None and headers.activity_type != ActivityTypeEnum.Process):
            raise Exception(f'Not a valid action for a event [{headers.action}] expected [{ActivityTypeEnum.Process}]')

        handler = self.event_subscribers[headers.dispatcher]
        request =  self.json_worker.convert_json_to_class(json_content, handler.request_type)
            
        response_object = await handler.process(request=request, processing_context=processing_context, unit_of_work=unit_of_work)        
        
        return response_object


