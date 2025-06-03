import uuid

from typing import Optional
from pydantic import BaseModel, UUID4

class RaiseCommandRequest(BaseModel):    
    
    ApplicationName:str
    CommandName: str
    CommandVersion: Optional[str] = None
    CommandReference: Optional[str] = None
    Content: Optional[str] = None
    ItemsRemainingAtSource: Optional[int] = None
    Priority:Optional[int] = None
    SourceTraceMessageId: Optional[str] = None
    UniqueRequestHeaderHash: Optional[str] = None       

    @staticmethod
    def Create( 
            application_name: str,
            command_name: str,
            command_version: Optional[str] = None,
            command_reference: Optional[str] = None,
            content: Optional[str] = None,
            items_at_source:Optional[int] = None,
            priority: Optional[int] = None,
            source_trace_message_id:Optional[str] = None,
            unique_request_header_hash: Optional[str] = None): 
        
        return RaiseCommandRequest(
            ApplicationName=application_name,
            CommandName=command_name,
            CommandVersion = command_version,
            CommandReference = command_reference,
            Content = content,
            ItemsRemainingAtSource=items_at_source,
            Priority = priority,
            SourceTraceMessageId=source_trace_message_id,
            UniqueRequestHeaderHash = unique_request_header_hash            
        )
