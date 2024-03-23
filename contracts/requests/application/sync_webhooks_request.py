from typing import List
from pydantic import BaseModel
from orchestrator_sdk.contracts.requests.webhooks.webhook_request import WebhookRequest

class SyncWebhooksRequest(BaseModel):    
    
    ApplicationName: str
    Webhooks: List[WebhookRequest]

    @staticmethod
    def Create(application_name:str, webhooks:List[WebhookRequest]):
        
        return SyncWebhooksRequest(
            ApplicationName = application_name,
            Webhooks = webhooks  
        )
