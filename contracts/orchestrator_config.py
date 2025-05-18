from typing import Optional

class Webhook():
    name:str = None
    url:str = None
    api_token:Optional[str] = None

class OrchestratorConfig():    
    application_name:str = None
    base_url:str = None
    outbox_concurrency:int = None
    outbox_batch_size:int = None
    default_callback_webhook:Webhook = None
