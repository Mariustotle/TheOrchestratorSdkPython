
from pydantic import BaseModel
from typing import Optional

class PublisherRequest(BaseModel):    
    
    EventName: str = None
    LatestVersion: Optional[str] = None    
    JsonSchema: str = None

    def Create(self, event_name:[str], jason_schema:[str], latest_version:Optional[str] = None):
        self.EventName = event_name
        self.LatestVersion = latest_version
        self.JsonSchema = jason_schema
        
        return self