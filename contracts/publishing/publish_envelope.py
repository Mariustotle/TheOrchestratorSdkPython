from typing import Optional
from pydantic import BaseModel

class PublishEnvelope(BaseModel):
    endpoint:str = None
    handler:str = None
    reference:Optional[str] = None
    publish_request:Optional[object] = None
    source_message_id:Optional[str] = None
    group_trace_key:Optional[str] = None
    
    ## TODO: Remove trace data from payload into envolope level data to be passed in the header not body    
    
    def Create(self, publish_request:object, endpoint:str, handler:str, reference:Optional[str] = None, source_message_id:Optional[str] = None, group_trace_key:Optional[str] = None):
        self.publish_request = publish_request
        self.endpoint = endpoint
        self.handler = handler,
        self.reference = reference,
        self.source_message_id = source_message_id
        self.group_trace_key = group_trace_key    

        return self
    
    
    
    