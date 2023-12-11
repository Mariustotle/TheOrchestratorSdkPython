from typing import Optional, List
from pydantic import BaseModel
from orchestrator_sdk.contracts.requests.webhooks.webhook_request import WebhookRequest

class SyncWebhooksRequest(BaseModel):    
    
    ApplicationName: str = None
    Webhooks: List[WebhookRequest] = None

    def Create(self, application_name:[str], webhooks:List[WebhookRequest]):
        self.ApplicationName = application_name
        self.Webhooks = webhooks

        return self