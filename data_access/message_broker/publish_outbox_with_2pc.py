from typing import Optional
from datetime import datetime, timedelta
from orchestrator_sdk.seedworks.logger import Logger
from orchestrator_sdk.data_access.message_broker.message_broker_publisher_interface import MessageBrokerPublisherInterface
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope
from orchestrator_sdk.data_access.database.unit_of_work import UnitOfWork
from orchestrator_sdk.data_access.database.entities.message_outbox_entity import MessageOutboxEntity

logger = Logger.get_instance()

class PublishOutboxWith2PC(MessageBrokerPublisherInterface):
    de_dup_delay_in_minutes:int = 30
    
    def _get_value_from_pydantic_property(self, pyprop):
        if (pyprop == None or len(pyprop) < 1):
            return None
            
        return pyprop[0]
    
    async def publish(self, publish_instruction:PublishEnvelope, unit_of_work:Optional[UnitOfWork] = None):
        try:                   
            
            if unit_of_work == None:
                raise Exception(f'To use the OutboxWith2PC publisher you need to impliment a UnitOfWork context')
            
            eligible_after = None            
            if publish_instruction.de_duplication_enabled and publish_instruction.unique_header is not None:
                delay_period = timedelta(minutes=self.de_dup_delay_in_minutes)
                eligible_after = datetime.utcnow + delay_period            
            
            delay_period = timedelta(minutes=self.de_dup_delay_in_minutes)
            
            pending_message = MessageOutboxEntity.Create(
                handler_name = publish_instruction.handler_name,
                endpoint=publish_instruction.endpoint,
                publish_request_object=publish_instruction.publish_request,
                source_message_trace_id=publish_instruction.source_message_trace_id,
                de_duplication_enabled=publish_instruction.de_duplication_enabled,
                unique_header=publish_instruction.unique_header, message_name=publish_instruction.message_name,
                priority=publish_instruction.priority, eligible_after=eligible_after)

            # Save to local SQLLite database with status Pending with the [transaction_number] above
            await unit_of_work.message_outbox_repository.add_message(pending_message)
        
        except Exception as ex:
            
            logger.error(ex)            
            raise

