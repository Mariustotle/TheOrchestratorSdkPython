import uuid
 
from typing import Optional
from pydantic import BaseModel, UUID4

class PublishEnvelope(BaseModel):
    endpoint:str
    handler_name:str
    message_name:str
    de_duplication_enabled:bool
    unique_header:Optional[str]
    reference:Optional[str] = None
    publish_request:Optional[object] = None
    source_message_trace_id:Optional[str] = None    
    priority:Optional[int] = None    

    ## TODO: Remove trace data from payload into envolope level data to be passed in the header not body    
    
    @staticmethod
    def Create( 
            publish_request:object, 
            endpoint:str, 
            message_name:str,
            handler_name:str, 
            reference:Optional[str] = None, 
            source_message_trace_id:Optional[str] = None, 
            priority:Optional[int] = None, 
            de_duplication_enabled:bool = None, 
            unique_header:Optional[str] = None):
        
        return PublishEnvelope(
            publish_request = publish_request,
            endpoint = endpoint,
            message_name = message_name,
            handler_name = handler_name,
            reference = reference,
            source_message_trace_id = source_message_trace_id,
            priority = priority,
            de_duplication_enabled = de_duplication_enabled if de_duplication_enabled is not None else False,
            unique_header = unique_header
        )
