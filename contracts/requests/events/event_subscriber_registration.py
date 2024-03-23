
from pydantic import BaseModel
from typing import Optional

class EventSubscriberRegistration(BaseModel):    
    
    EventName: str = None
    WebhookName: str = None
    
    EventVersion: Optional[str] = None
    Dispatcher: Optional[str] = None    
    MaxConcurrency: Optional[int] = None

    def Create(self, event_name:str, dispatcher:Optional[str], webhook_name:str, 
               event_version:Optional[str] = None, max_concurrency: Optional[int] = None):
        self.EventName = event_name
        self.Dispatcher = dispatcher
        self.WebhookName = webhook_name
        self.EventVersion = event_version
        self.MaxConcurrency = max_concurrency
        
        return self