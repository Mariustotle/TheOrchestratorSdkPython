from typing import List, Optional
from pydantic import BaseModel

from orchestrator_sdk.contracts.requests.events.event_publisher_registration import EventPublisherRegistration
from orchestrator_sdk.contracts.requests.events.event_subscriber_registration import EventSubscriberRegistration

class ApplicationSyncRequest(BaseModel):    
    ApplicationName: str = None
    EventPublishers: Optional[List[EventPublisherRegistration]] = None
    EventSubscribers: Optional[List[EventSubscriberRegistration]] = None

    def Create(application_name:str, event_publishers:Optional[List[EventPublisherRegistration]], 
               event_subscribers:Optional[List[EventSubscriberRegistration]]):
        
        return ApplicationSyncRequest(
            ApplicationName = application_name,
            EventPublishers = event_publishers,
            EventSubscribers = event_subscribers         
        )
