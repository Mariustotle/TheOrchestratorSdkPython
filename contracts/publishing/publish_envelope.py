import uuid
 
from typing import Optional
from pydantic import BaseModel, UUID4

class PublishEnvelope(BaseModel):
    endpoint:str
    handler_name:str
    reference:Optional[str] = None
    publish_request:Optional[object] = None
    source_message_trace_id:Optional[str] = None
    priority:Optional[int] = None    

    ## TODO: Remove trace data from payload into envolope level data to be passed in the header not body    
    
    @staticmethod
    def Create( 
            publish_request:object, 
            endpoint:str, 
            handler_name:str, 
            reference:Optional[str] = None, 
            source_message_trace_id:Optional[str] = None, 
            priority:Optional[int] = None):
        
        return PublishEnvelope(
            publish_request = publish_request,
            endpoint = endpoint,
            handler_name = handler_name,
            reference = reference,
            source_message_trace_id = source_message_trace_id,
            priority = priority            
        )

    
    
    