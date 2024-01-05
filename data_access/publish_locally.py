from pydantic import UUID4
from typing import Optional, List
from seedworks.logger import Logger
from orchestrator_sdk.data_access.message_broker_publisher_interface import MessageBrokerPublisherInterface
from orchestrator_sdk.contracts.types.process_structure import ProcessStructure
from orchestrator_sdk.contracts.requests.commands.concurrent_command_request import ConcurrentCommandRequest
from orchestrator_sdk.contracts.requests.commands.queue_command_request import QueueCommandRequest
from orchestrator_sdk.contracts.requests.events.publish_event_request import PublishEventRequest
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope

import requests
import json

logger = Logger.get_instance()

class PublishLocally(MessageBrokerPublisherInterface):
    
    def _publish_concurrent_command_locally(self, request:ConcurrentCommandRequest):
        pass
    
    def _publish_queue_command_locally(self, request:QueueCommandRequest):
        pass
    
    def _publish_concurrent_event_locally(self, request:PublishEventRequest):
        pass
    

    async def publish(self, publish_instruction:PublishEnvelope, transaction_reference:Optional[UUID4] = None):
        try:
            
            ## TODO: Dunamically identify the Process Structure
            processing_type = ProcessStructure

            if isinstance(publish_instruction.publish_request, ConcurrentCommandRequest):
                self._publish_concurrent_command_locally(publish_instruction.publish_request)
            elif isinstance(publish_instruction.publish_request, QueueCommandRequest):
                self._publish_queue_command_locally(publish_instruction.publish_request)
            elif isinstance(publish_instruction.publish_request, PublishEventRequest):
                self._publish_concurrent_event_locally(publish_instruction.publish_request)
            else:
                raise Exception(f'Unable to locally publish message, unsupported request [{type(publish_instruction.publish_request)}] received. {publish_instruction.handler}')

        except Exception as ex:
            
            logger.error(ex)            
            raise

    async def completed(self, transaction_reference:Optional[UUID4] = None):
        pass
