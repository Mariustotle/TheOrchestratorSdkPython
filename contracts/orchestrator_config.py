from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Webhook():
    name:str = None
    url:str = None
    api_token:Optional[str] = None

@dataclass
class OrchestratorConfig():
    application_hash:str = None ## Used to uniquely identify an application
    base_url:str = None    
    process_locally:bool = None
    default_callback_webhook:Webhook = None
    application_name:str = None
