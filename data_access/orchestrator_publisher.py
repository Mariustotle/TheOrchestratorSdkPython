from seedworks.logger import Logger
from typing import Optional
from requests import Response

import requests
import json

logger = Logger.get_instance()

class OrchestratorPublisher():    
    
    def _post(self, url:str, request) -> Response:
        
        headers = {'Content-Type': 'application/json'}      
        json_data = json.dumps(json.loads(request.json()))
        response = requests.post(url, data=json_data, headers=headers, verify=False)
        
        return response        
        
    
    async def post(self, request, url:str, description:Optional[str] = "N/A", reference:Optional[str] = "N/A") -> Optional[str]:        
        
        try:

            response:Response = self._post(url, request)
            
            if not response.ok:
                raise Exception(f"Failed to post [{description}] with reference [{reference}] to [{url}] with ErrorCode [{response.status_code}]. Error Details >> {response.content}")
            
            logger.info(f'Successfully posted [{description}] with reference [{reference}] to the orchestrator')
            
            return response

        except Exception as ex:
            
            logger.error(ex)            
            raise

        
        
    
