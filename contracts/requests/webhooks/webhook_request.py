
from pydantic import BaseModel
from typing import Optional

class WebhookRequest(BaseModel):    
    
    Name: str
    WebhookUrl: str
    ApiToken: Optional[str] = None

    @staticmethod
    def Create(name:str, webhook_url:str,  api_token:Optional[str] = None):
        
        return WebhookRequest(
            Name = name,
            WebhookUrl = webhook_url,
            ApiToken = api_token 
        )
