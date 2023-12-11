from typing import Optional, List
from pydantic import BaseModel
from orchestrator_sdk.contracts.requests.events.subscriber_request import SubscriberRequest

class SyncEventSubscription(BaseModel):    
    
    ApplicationName: str = None
    Subscriptions: List[SubscriberRequest] = None

    def Create(self, application_name:[str], subscriptions:List[SubscriberRequest]):
        self.ApplicationName = application_name
        self.Subscriptions = subscriptions

        return self
