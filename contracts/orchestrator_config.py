from typing import Optional

class Webhook():
    name:str = None
    url:str = None
    api_token:Optional[str] = None

class OrchestratorConfig():
    base_url:str = None    
    default_callback_webhook:Webhook = None
    application_name:str = None
