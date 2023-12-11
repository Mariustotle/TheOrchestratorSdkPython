
from pydantic import BaseModel
from typing import Optional

class SubscriberRequest(BaseModel):    
    
    EventName: str = None
    EventVersion: Optional[str] = None
    DispatcherName: Optional[str] = None
    WebhookName: str = None

    def Create(self, event_name:[str], dispatcher_name:Optional[str], webhook_name:[str], event_version:Optional[str] = None):
        self.EventName = event_name
        self.DispatcherName = dispatcher_name
        self.WebhookName = webhook_name
        self.EventVersion = event_version
        
        return self