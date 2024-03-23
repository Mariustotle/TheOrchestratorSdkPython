
from pydantic import BaseModel
from typing import Optional

from orchestrator_sdk.contracts.types.process_type import ProcessType

class EventPublisherRegistration(BaseModel):    
    
    EventName: str = None    
    ProcessingType: ProcessType = None
    
    LatestVersion: Optional[str] = None
    DeDuplicationEnabled: Optional[bool]
    JsonSchema: Optional[str] = None
    ItemsRemainingAtSource: Optional[int] = None
    AllowPublishingWithoutSubscribers: Optional[bool] = None
    RequiresSubscriberApproval: Optional[bool] = None    

    def Create(event_name:str, processing_type: ProcessType, latest_version:Optional[str] = None, jason_schema:Optional[str] = None,
               de_duplication_enabled:Optional[bool] = None, items_remaining_at_source: Optional[int] = None,
               allow_publishing_without_subscribers: Optional[bool] = None, require_subscriber_approval: Optional[bool] = None):
        
        return EventPublisherRegistration(
            EventName=event_name,
            ProcessingType=processing_type,
            LatestVersion=latest_version,
            JsonSchema=jason_schema,
            DeDuplicationEnabled=de_duplication_enabled,
            ItemsRemainingAtSource=items_remaining_at_source,
            AllowPublishingWithoutSubscribers=allow_publishing_without_subscribers,
            RequiresSubscriberApproval=require_subscriber_approval)
