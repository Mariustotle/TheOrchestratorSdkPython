from typing import Optional

class Webhook():
    name:str = None
    url:str = None
    api_token:Optional[str] = None

class Outbox():
    concurrency:int = None
    batch_size:int = None
    item_delay:float = None
    long_delay:int = None

class OrchestratorConfig():    
    application_name:str = None
    base_url:str = None
    outbox:Outbox = None
    default_callback_webhook:Webhook = None
