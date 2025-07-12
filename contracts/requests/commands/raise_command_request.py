from typing import Optional
from pydantic import BaseModel

from uuid import UUID
from orchestrator_sdk.callback.processing_context import ProcessingContext

class RaiseCommandRequest(BaseModel):    
    ApplicationName:str
    CommandName: str
    CommandVersion: Optional[str] = None
    CommandReference: Optional[str] = None
    Content: Optional[str] = None
    ItemsRemainingAtSource: Optional[int] = None
    GroupTraceKey: Optional[UUID] = None
    Priority:Optional[int] = None
    SourceTraceMessageId: Optional[UUID] = None
    SourceMapMessageId: Optional[UUID] = None
    UniqueRequestHeaderHash: Optional[str] = None       

    @staticmethod
    def Create( 
            processing_context:ProcessingContext,
            application_name: str,
            command_name: str,
            command_version: Optional[str] = None,
            command_reference: Optional[str] = None,
            content: Optional[str] = None,
            items_at_source:Optional[int] = None,
            priority: Optional[int] = None,
            unique_request_header_hash: Optional[str] = None): 
        
        return RaiseCommandRequest(
            ApplicationName = application_name,
            CommandName = command_name,
            CommandVersion = command_version,
            CommandReference = command_reference,
            Content = content,
            ItemsRemainingAtSource = items_at_source,
            Priority = priority,
            SourceTraceMessageId = processing_context.source_message_trace_id,
            GroupTraceKey = processing_context.group_trace_key,
            SourceMapMessageId = processing_context.source_map_message_id,
            UniqueRequestHeaderHash = unique_request_header_hash            
        )
