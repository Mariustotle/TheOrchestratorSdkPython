import uuid

from typing import Optional
from pydantic import BaseModel, UUID4

class RaiseCommandRequest(BaseModel):    
    
    ApplicationName:str
    CommandName: str
    CommandVersion: Optional[str] = None
    CommandReference: Optional[str] = None
    Content: Optional[str] = None
    Priority:Optional[int] = None
    SourceTraceMessageId: Optional[str] = None
    UniqueRequestHeader: Optional[str] = None       

    @staticmethod
    def Create( 
            application_name: str,
            command_name: str,
            command_version: Optional[str] = None,
            command_reference: Optional[str] = None,
            content: Optional[str] = None,
            priority: Optional[int] = None,
            source_trace_message_id: Optional[str] = None,
            unique_request_header: Optional[str] = None): 
        
        return RaiseCommandRequest(
            ApplicationName=application_name,
            CommandName=command_name,
            CommandVersion = command_version,
            CommandReference = command_reference,
            Content = content,
            Priority = priority,
            SourceTraceMessageId = source_trace_message_id,
            UniqueRequestHeader=unique_request_header            
        )
