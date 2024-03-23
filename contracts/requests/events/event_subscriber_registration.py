from pydantic import BaseModel
from typing import Optional

class EventSubscriberRegistration(BaseModel):    
    
    EventName: str
    WebhookName: str
    
    EventVersion: Optional[str] = None
    Dispatcher: Optional[str] = None    
    MaxConcurrency: Optional[int] = None

    @staticmethod
    def Create(event_name:str, webhook_name:str, dispatcher:Optional[str],  
               event_version:Optional[str] = None, max_concurrency: Optional[int] = None):
        
        return EventSubscriberRegistration (
            EventName = event_name,
            Dispatcher = dispatcher,
            WebhookName = webhook_name,
            EventVersion = event_version,
            MaxConcurrency = max_concurrency
        )
