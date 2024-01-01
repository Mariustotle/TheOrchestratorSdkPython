from typing import Optional
from pydantic import BaseModel

class SuccessEventDetails(BaseModel):    
    
    EventName:str = None
    EventVersion: Optional[str] = None

    def Create (self, 
               event_name:str,
               event_version:Optional[str]):       

        self.EventName = event_name
        self.EventVersion = event_version
     
        return self 