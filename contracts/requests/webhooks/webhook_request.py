
from pydantic import BaseModel
from typing import Optional

class WebhookRequest(BaseModel):    
    
    Name: str = None
    WebhookUrl: str = None
    ApiToken: Optional[str] = None

    def Create(self, name:[str], webhook_url:[str],  api_token:[str] = None):
        self.Name = name
        self.WebhookUrl = webhook_url
        self.ApiToken = api_token
        
        return self