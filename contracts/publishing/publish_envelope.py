from typing import Optional
from pydantic import BaseModel
from orchestrator_sdk.callback.processing_context import ProcessingContext

class PublishEnvelope(BaseModel):
    endpoint: str
    handler_name: str
    message_name: str
    de_duplication_enabled: bool
    de_duplication_delay_in_minutes: int
    processing_context: ProcessingContext
    unique_header_hash: Optional[str]
    reference:Optional[str] = None
    publish_request: Optional[object] = None
    priority: Optional[int] = None
        
    @staticmethod
    def Create( 
            publish_request: object, 
            endpoint: str, 
            message_name: str,
            handler_name: str, 
            processing_context: ProcessingContext,
            reference: Optional[str] = None, 
            priority: Optional[int] = None, 
            de_duplication_enabled: Optional[bool] = None,
            de_duplication_delay_in_seconds: Optional[int] = None,            
            unique_header_hash: Optional[str] = None):
        
        if de_duplication_enabled and unique_header_hash is None:
            raise Exception(f"Unable to publish message, De Duplication is enabled but there is no Unique Header provided. Message Name=[{message_name}], Handler Name=[{handler_name}], Reference=[{reference}]")            
        
        return PublishEnvelope(
            publish_request = publish_request,
            endpoint = endpoint,
            message_name = message_name,
            handler_name = handler_name,
            reference = reference,
            priority = priority,
            processing_context = processing_context,
            de_duplication_enabled = de_duplication_enabled if de_duplication_enabled is not None else False,
            de_duplication_delay_in_minutes = de_duplication_delay_in_seconds if de_duplication_delay_in_seconds is not None else 0,
            unique_header_hash = unique_header_hash)
        
