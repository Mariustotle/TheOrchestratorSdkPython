from typing import Optional
from sdk.logging.logger import Logger
from orchestrator_sdk.data_access.message_broker.message_broker_publisher_interface import MessageBrokerPublisherInterface
from orchestrator_sdk.contracts.types.process_structure import ProcessStructure
from orchestrator_sdk.contracts.requests.commands.raise_command_request import RaiseCommandRequest
from orchestrator_sdk.contracts.requests.events.publish_event_request import PublishEventRequest
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope
from orchestrator_sdk.data_access.database.unit_of_work import UnitOfWork

import requests
import json

logger = Logger.get_instance()

class PublishLocally(MessageBrokerPublisherInterface):
    
    def _publish_command_locally(self, request:RaiseCommandRequest):
        pass    
   
    def _publish_event_locally(self, request:PublishEventRequest):
        pass
    

    async def publish(self, publish_instruction:PublishEnvelope, unit_of_work:Optional[UnitOfWork] = None):
        try:

            if isinstance(publish_instruction.publish_request, RaiseCommandRequest):
                self._publish_command_locally(publish_instruction.publish_request)
                
            elif isinstance(publish_instruction.publish_request, PublishEventRequest):
                self._publish_event_locally(publish_instruction.publish_request)
            else:
                raise Exception(f'Unable to locally publish message, unsupported request [{type(publish_instruction.publish_request)}] received. {publish_instruction.handler}')

        except Exception as ex:
            
            logger.error(ex)            
            raise

    async def completed(self):
        pass
