from typing import List
from pydantic import BaseModel

from orchestrator_sdk.contracts.requests.events.event_publisher_registration import EventPublisherRegistration
from orchestrator_sdk.contracts.requests.events.event_subscriber_registration import EventSubscriberRegistration
from orchestrator_sdk.contracts.requests.commands.command_raiser_registration import CommandRaiserRegistration
from orchestrator_sdk.contracts.requests.commands.command_processor_registration import CommandProcessorRegistration
from orchestrator_sdk.contracts.requests.stream.stream_subscriber_registration import StreamSubscriberRegistration

class ApplicationSyncRequest(BaseModel):    
    ApplicationName: str = None
    EventPublishers: List[EventPublisherRegistration] = None
    EventSubscribers: List[EventSubscriberRegistration] = None
    CommandRaisers: List[CommandRaiserRegistration] = None
    CommandProcessors: List[CommandProcessorRegistration] = None
    StreamSubscribers: List[StreamSubscriberRegistration] = None

    @staticmethod
    def Create(application_name:str, event_publishers:List[EventPublisherRegistration], 
               event_subscribers:List[EventSubscriberRegistration],
               command_raisers:List[CommandRaiserRegistration],
               command_processors:List[CommandProcessorRegistration],
               stream_subscribers:List[StreamSubscriberRegistration]
               ):
        
        return ApplicationSyncRequest(
            ApplicationName = application_name,
            EventPublishers = event_publishers,
            EventSubscribers = event_subscribers,
            CommandRaisers = command_raisers,
            CommandProcessors = command_processors,
            StreamSubscribers = stream_subscribers
        )
