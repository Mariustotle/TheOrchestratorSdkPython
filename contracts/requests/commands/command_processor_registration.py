from pydantic import BaseModel
from typing import Optional
from orchestrator_sdk.contracts.types.processing_type import ProcessingType

class CommandProcessorRegistration(BaseModel):    
    CommandName: str
    WebhookName: str
    ProcessingType: ProcessingType
    
    LatestVersion: Optional[str] = None    
    Dispatcher: Optional[str] = None
    JsonSchema: Optional[str] = None 
    MaxConcurrency: Optional[int] = None
    NewCommandRaisersRequireApproval: Optional[bool] = None
    DeDuplicationEnabled: Optional[bool] = None
    DeDuplicationDelayInMinutes: Optional[int] = None

    @staticmethod
    def Create(command_name:str, webhook_name:str, procesing_type, dispatcher:Optional[str] = None, json_schema:Optional[str] = None,
               latest_version = None, max_concurrency: Optional[int] = None, requires_command_raiser_approval: Optional[bool] = None,
               de_duplication_enabled:Optional[bool] = None, de_duplication_delay_in_minutes: Optional[int] = None):
        
        return CommandProcessorRegistration (
            CommandName = command_name,
            ProcessingType = procesing_type,
            Dispatcher = dispatcher,
            WebhookName = webhook_name,
            LatestVersion = latest_version,
            JsonSchema = json_schema,
            NewCommandRaisersRequireApproval = requires_command_raiser_approval,
            DeDuplicationEnabled = de_duplication_enabled,
            DeDuplicationDelayInMinutes=de_duplication_delay_in_minutes,
            MaxConcurrency = max_concurrency
        )
