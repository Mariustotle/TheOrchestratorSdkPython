
from pydantic import BaseModel
from typing import Optional

class SubscriberRequest(BaseModel):    
    
    EventName: str = None
    EventVersion: Optional[str] = None
    Dispatcher: Optional[str] = None
    WebhookName: str = None

    def Create(self, event_name:[str], dispatcher:Optional[str], webhook_name:[str], event_version:Optional[str] = None):
        self.EventName = event_name
        self.Dispatcher = dispatcher
        self.WebhookName = webhook_name
        self.EventVersion = event_version
        
        return self