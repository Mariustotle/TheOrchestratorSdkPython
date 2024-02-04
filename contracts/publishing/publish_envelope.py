from typing import Optional
from pydantic import BaseModel

class PublishEnvelope(BaseModel):
    endpoint:str = None
    handler_name:str = None
    reference:Optional[str] = None
    publish_request:Optional[object] = None
    source_trace_message_id:Optional[str] = None
    priority:Optional[int] = None    
    
    ## TODO: Remove trace data from payload into envolope level data to be passed in the header not body    
    
    def Create(self, 
            publish_request:object, 
            endpoint:str, 
            handler_name:str, 
            reference:Optional[str] = None, 
            source_trace_message_id:Optional[str] = None, 
            priority:Optional[int] = None):
        
        self.publish_request = publish_request
        self.endpoint = endpoint
        self.handler_name = handler_name,
        self.reference = reference,
        self.source_trace_message_id = source_trace_message_id

        self.priority = priority

        return self
    
    
    
    