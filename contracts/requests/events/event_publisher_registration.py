
from pydantic import BaseModel
from typing import Optional

from orchestrator_sdk.contracts.types.process_type import PublishAdapter

class EventPublisherRegistration(BaseModel):    
    
    EventName: str = None    
    ProcessingType: int = None
    
    LatestVersion: Optional[str] = None
    DeDuplicationEnabled: Optional[bool]
    JsonSchema: Optional[str] = None
    ItemsRemainingAtSource: Optional[int] = None
    AllowPublishingWithoutSubscribers: Optional[bool] = None
    RequiresSubscriberApproval: Optional[bool] = None
    

    def Create(self, event_name:str, processing_type: PublishAdapter, latest_version:Optional[str] = None, jason_schema:Optional[str] = None,
               de_duplication_enabled:Optional[bool] = False, items_remaining_at_source: Optional[int] = None,
               allow_publishing_without_subscribers: Optional[bool] = None, require_subscriber_approval: Optional[bool] = None):
        
        self.EventName = event_name
        self.ProcessingType = processing_type,
        self.LatestVersion = latest_version
        self.DeDuplicationEnabled = de_duplication_enabled,
        self.JsonSchema = jason_schema
        self.ItemsRemainingAtSource = items_remaining_at_source,
        self.AllowPublishingWithoutSubscribers = allow_publishing_without_subscribers,
        self.RequiresSubscriberApproval = require_subscriber_approval
        
        return self