from typing import Optional
from orchestrator_sdk.seedworks.logger import Logger
from orchestrator_sdk.data_access.message_broker.message_broker_publisher_interface import MessageBrokerPublisherInterface
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope
from orchestrator_sdk.callback_context import CallbackContext
from orchestrator_sdk.data_access.local_persistance.unit_of_work import UnitOfWork
from orchestrator_sdk.data_access.local_persistance.entities.message_outbox_entity import MessageOutboxEntity

logger = Logger.get_instance()

class PublishOutboxWith2PC(MessageBrokerPublisherInterface):
    
    def _get_value_from_pydantic_property(self, pyprop):
        if (pyprop == None or len(pyprop) < 1):
            return None
            
        return pyprop[0]      
    
    async def publish(self, publish_instruction:PublishEnvelope, unit_of_work:Optional[UnitOfWork] = None):
        try:                   
            
            if unit_of_work == None:
                raise Exception(f'To use the OutboxWith2PC publisher you need to impliment a UnitOfWork context')
            
            pending_message = MessageOutboxEntity().Create(
                # TODO: Why is the pydantic class not converting properly for this specific property?
                handler_name = self._get_value_from_pydantic_property(publish_instruction.handler_name),
                endpoint=publish_instruction.endpoint,
                publish_request_object=publish_instruction.publish_request,
                source_message_id=publish_instruction.source_message_id,
                group_trace_key=publish_instruction.group_trace_key)

            # Save to local SQLLite database with status Pending with the [transaction_number] above
            await unit_of_work.message_outbox_repository.add_message(pending_message)
        
        except Exception as ex:
            
            logger.error(ex)            
            raise

