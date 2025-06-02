from pydantic import BaseModel
from typing import Optional

class StreamSubscriberRegistration(BaseModel):    
    StreamName: str
    WebhookName: str
    
    Version: Optional[str] = None
    Dispatcher: Optional[str] = None    

    @staticmethod
    def Create(stream_name:str, webhook_name:str, dispatcher:Optional[str],  
               version:Optional[str] = None):
        
        return StreamSubscriberRegistration (
            StreamName = stream_name,
            Dispatcher = dispatcher,
            WebhookName = webhook_name,
            Version = version
        )

