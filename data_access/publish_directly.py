from pydantic import UUID4
from typing import Optional, List
from seedworks.logger import Logger
from requests import Response
from orchestrator_sdk.data_access.message_broker_publisher_interface import MessageBrokerPublisherInterface
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope

import requests
import json

logger = Logger.get_instance()

class PublishDirectly(MessageBrokerPublisherInterface):

    async def publish(self, publish_instruction:PublishEnvelope, transaction_reference:Optional[UUID4] = None):
        
        try:            
            headers = {'Content-Type': 'application/json'}      
            json_data = json.dumps(json.loads(publish_instruction.publish_request.json()))
            http_response:Response = requests.post(publish_instruction.endpoint, data=json_data, headers=headers, verify=False)           
            
            if not http_response.ok:
                raise Exception(f"Failed to post on behalf of [{publish_instruction.handler}] to [{publish_instruction.endpoint}] with ErrorCode [{http_response.status_code}]. Error Details >> {http_response.content}")
            
            logger.info(f'Successfully posted on behalf of [{publish_instruction.handler}] to the orchestrator - reference [{publish_instruction.reference}]')

        except Exception as ex:
            logger.error(ex)            
            raise


    async def completed(self, transaction_reference:Optional[UUID4] = None):
        pass