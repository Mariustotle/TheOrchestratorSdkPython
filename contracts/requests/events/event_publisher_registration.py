
from pydantic import BaseModel
from typing import Optional

from orchestrator_sdk.contracts.types.processing_type import ProcessingType

class EventPublisherRegistration(BaseModel):    
    
    EventName: str    
    ProcessingType: ProcessingType
    
    LatestVersion: Optional[str] = None
    DeDuplicationEnabled: Optional[bool] = None
    DeDuplicationDelayInMinutes: Optional[int] = None
    JsonSchema: Optional[str] = None
    ItemsRemainingAtSource: Optional[int] = None
    AllowPublishingWithoutSubscribers: Optional[bool] = None
    NewEventSubscriberRequiresApproval: Optional[bool] = None   
    MaxConcurrency: Optional[int] = None 

    @staticmethod
    def Create(event_name:str, processing_type: ProcessingType, latest_version:Optional[str] = None, json_schema:Optional[str] = None,
               de_duplication_enabled:Optional[bool] = None, items_remaining_at_source: Optional[int] = None, allow_publishing_without_subscribers: Optional[bool] = None,
                max_concurrency: Optional[int] = None, require_new_subscriber_approval: Optional[bool] = None, de_duplication_delay_in_minutes: Optional[int] = None):
        
        return EventPublisherRegistration(
            EventName=event_name,
            ProcessingType=processing_type,
            LatestVersion=latest_version,
            JsonSchema=json_schema,
            DeDuplicationEnabled=de_duplication_enabled,
            DeDuplicationDelayInMinutes=de_duplication_delay_in_minutes,
            ItemsRemainingAtSource=items_remaining_at_source,
            AllowPublishingWithoutSubscribers=allow_publishing_without_subscribers,
            MaxConcurrency=max_concurrency,
            NewEventSubscriberRequiresApproval=require_new_subscriber_approval)
