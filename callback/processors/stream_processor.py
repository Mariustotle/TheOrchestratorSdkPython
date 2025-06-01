from orchestrator_sdk.callback.processors.processor_base import ProcessorBase
from orchestrator_sdk.data_access.database.unit_of_work import UnitOfWork
from orchestrator_sdk.callback.processing_context import ProcessingContext
from orchestrator_sdk.callback.stream_context import StreamContext
from orchestrator_sdk.callback.callback_types.stream_event_callback import StreamEventCallback, StreamHeaders
from orchestrator_sdk.message_processors.StreamOutbound.stream_subscriber_base import StreamSubscriberBase
from orchestrator_sdk.callback.header_properties import HeaderProperties
from orchestrator_sdk.contracts.types.action_type import ActionType


class StreamProcessor(ProcessorBase):
    callback_headers: StreamHeaders = None
    stream_subscribers: dict[str, StreamSubscriberBase] = {} 
    
    def __init__(self, application_name:str, stream_subscribers): 
        self.stream_subscribers = stream_subscribers
        ProcessorBase.__init__(self, application_name)

    def get_header_properties(self, headers:HeaderProperties) -> StreamHeaders:
        return StreamHeaders.Create(
            message_trace_id_string=headers.trace_message_id,
            message_id_string=headers.message_id,
            message_name=headers.message_name,
            application_name=headers.application_name,
            dispatcher=headers.dispatcher,
            action_string=headers.action,
            message_type_string=headers.message_type,
            reference=headers.reference,
            priority_string=headers.priority
        )
    
    def get_processing_context(self, headers:StreamHeaders) -> ProcessingContext: 
        return ProcessingContext.Create(source_message_trace_id=headers.message_trace_id, source_priority=headers.priority, message_name=headers.message_name, reference=headers.reference)

    async def process_specific(self, json_content, callback: StreamEventCallback, headers:StreamHeaders, processing_context:ProcessingContext, unit_of_work:UnitOfWork) -> object:
        response_object = None

        if (headers.action != None and headers.action != ActionType.Process):
            raise Exception(f'Not a valid action for a stream [{headers.action}] expected [{ActionType.Process}]')
        
        stream_context = StreamContext.Create(action=callback.Action, event_id=callback.EventId, stream_identifier=callback.StreamIdentifier,
                is_latest=callback.IsLatest, official_created_date=callback.OfficialCreatedDate, 
                effective_from_date=callback.EffectiveFromDate, effective_to_date=callback.EffectiveToDate)
        
        handler = self.stream_subscribers[headers.dispatcher]
        request =  self.json_worker.convert_json_to_class(json_content, handler.request_type)
            
        response_object = await handler.process(request=request, processing_context=processing_context, 
            stream_context=stream_context, unit_of_work=unit_of_work)  
              
        return response_object





