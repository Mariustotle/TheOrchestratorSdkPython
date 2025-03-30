from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope
from requests import Response
from sdk.logging.logger import Logger

logger = Logger.get_instance()

import requests
import json

class ApiSubmission:
    
    def get_json_data(self, publish_request:object):
        converted = None        
        
        if (isinstance(publish_request, dict)):
            converted = publish_request 
        elif (isinstance(publish_request, str)):
            converted = publish_request
        else:
           converted = json.dumps(json.loads(publish_request.publish_request.json()))
        
        return converted
        
    
    async def submit(self, publish_request:PublishEnvelope):
        
        try:
            
            json_data = self.get_json_data(publish_request.publish_request)
            
            headers = {'Content-Type': 'application/json'}      
            
            http_response:Response = requests.post(publish_request.endpoint, data=json_data, headers=headers, verify=False)           
            
            if not http_response.ok:
                raise Exception(f"Failed to post on behalf of [{publish_request.handler_name}] to [{publish_request.endpoint}] with ErrorCode [{http_response.status_code}]. Error Details >> {http_response.content}")
            
            logger.success(f'Successfully posted on behalf of [{publish_request.handler_name}] to the orchestrator - reference [{publish_request.reference}]')

        except Exception as ex:
            logger.error(ex)            
            raise