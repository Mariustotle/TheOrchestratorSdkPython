from orchestrator_sdk.callback_context import CallbackContext
from orchestrator_sdk.message_processors.commands.command_processor_base import CommandProcessorBase
from orchestrator_sdk.message_processors.commands.command_raiser_base import CommandRaiserBase
from orchestrator_sdk.message_processors.events.event_publisher_base import EventPublisherBase
from orchestrator_sdk.message_processors.events.event_subscriber_base import EventSubscriberBase
from orchestrator_sdk.services.idempotence_service import IdempotenceService

from orchestrator_sdk.contracts.types.action_type import ActionType
from orchestrator_sdk.contracts.types.message_type import MessageType
from orchestrator_sdk.data_access.database.unit_of_work import UnitOfWork

from orchestrator_sdk.seedworks.json_worker import JsonWorker
from orchestrator_sdk.seedworks.logger import Logger

logger = Logger.get_instance()

import uuid

class CallbackProcessor:
    
    idempotence_service: IdempotenceService = None
    
    command_raisers: dict[str, CommandRaiserBase]
    command_processors: dict[str, CommandProcessorBase] = {} 
    event_subscribers: dict[str, EventSubscriberBase] = {}
    event_publishers: dict[str, EventPublisherBase] = {}
    application_name: str
    json_worker:JsonWorker = None

        
    def __init__(self, command_raisers, command_processors, event_subscribers, event_publishers): 
        self.command_raisers = command_raisers
        self.command_processors = command_processors
        self.event_subscribers = event_subscribers
        self.event_publishers = event_publishers
        self.idempotence_service = IdempotenceService()
        self.json_worker = JsonWorker()
   
    async def _process_command(self, processor_name:str, reference:str, command_name:str, action_type:ActionType, json_content, unit_of_work:UnitOfWork):        
        handler = self.command_processors[processor_name]
        
        if (action_type == ActionType.Process):
            request =  self.json_worker.convert_json_to_class(json_content, handler.request_type)
            return await handler.process(request=request, command_name=command_name, reference=reference, unit_of_work=unit_of_work)            
    
    async def _process_event(self, processor_name:str, reference:str, event_name:str, json_content, unit_of_work:UnitOfWork):        
        handler = self.event_subscribers[processor_name]        
        request = self.json_worker.convert_json_to_class(json_content, handler.request_type)
        return await handler.process(request=request, event_name=event_name, reference=reference, unit_of_work=unit_of_work)    
        
    async def process(self, json_payload, unit_of_work:UnitOfWork):        
       
        if (not CallbackContext.is_available()):
            raise Exception(f"Unable to process callback, please verify that you have added the [@init_callback_context_for_xxx] decoration to the API method")
        
        json_content = self.json_worker.read_as_json(json_payload)

        message_id:uuid = uuid.UUID(CallbackContext.message_id.get()) if CallbackContext.message_id.get() is not None else None
        if unit_of_work is not None:           
            already_processed:bool = await self.idempotence_service.has_message_been_processed(message_id=message_id, unit_of_work=unit_of_work)
            if already_processed:
                logger.info(f'Idempotence check: Message [{message_id}] have already been processed, skipping this request.')
                return # Our work here is done
        
        message_name:str = CallbackContext.message_name.get()   
        intented_application_name = CallbackContext.application_name.get()
        
        application_name_matched = self.application_name != None and intented_application_name != None and intented_application_name.lower() == self.application_name.lower()
        
        if (not application_name_matched):
            raise Exception(f"You are trying to process [{message_name}] that is intended for application [{intented_application_name}] on this application [{self.application_name}]")
        
        dispatcher:str = CallbackContext.dispatcher.get()        
        action_string = CallbackContext.action.get()
        action:ActionType = ActionType[action_string] 
        message_type_string = CallbackContext.message_type.get()
        message_type:str = MessageType[message_type_string]        
             
        reference:str = CallbackContext.reference.get()
        
        response_object = None
        
        if (message_type == MessageType.Command):            
            response_object = await self._process_command(
                processor_name=dispatcher, reference=reference, 
                command_name=message_name, action_type=action, json_content=json_content,
                unit_of_work=unit_of_work
            )
        
        elif (message_type == MessageType.Event):
            response_object = await self._process_event(
                processor_name=dispatcher, reference=reference, 
                event_name=message_name, json_content=json_content,
                unit_of_work=unit_of_work
            )
            
        if unit_of_work is not None: 
            await unit_of_work.message_history_repository.add_message(message_id)
            unit_of_work.message_session.commit()
            
        return response_object
