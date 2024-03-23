from typing import List
from pydantic import BaseModel

from orchestrator_sdk.contracts.requests.events.event_publisher_registration import EventPublisherRegistration
from orchestrator_sdk.contracts.requests.events.event_subscriber_registration import EventSubscriberRegistration

class ApplicationSyncRequest(BaseModel):    
    ApplicationName: str = None
    EventPublishers: List[EventPublisherRegistration] = None
    EventSubscribers: List[EventSubscriberRegistration] = None

    def Create(self, application_name:str, event_publishers:List[EventPublisherRegistration], event_subscribers:List[EventSubscriberRegistration]):
        self.ApplicationName = application_name
        self.EventPublishers = event_publishers
        self.EventSubscribers = event_subscribers

        return self