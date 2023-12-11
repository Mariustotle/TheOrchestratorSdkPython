from typing import List
from pydantic import BaseModel
from orchestrator_sdk.contracts.requests.events.publisher_request import PublisherRequest

class SyncEventPublishers(BaseModel):    
    
    ApplicationName: str = None
    Publishers: List[PublisherRequest] = None

    def Create(self, application_name:[str], publishers:List[PublisherRequest]):
        self.ApplicationName = application_name
        self.Publishers = publishers

        return self
