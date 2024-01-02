from typing import Optional
from pydantic import BaseModel, UUID4

class TracingData(BaseModel):    
    
    SourceMessageId: UUID4 = None
    GroupTraceKey: Optional[UUID4] = None

    def Create (self, 
               source_message_id:UUID4,
               group_trace_id:Optional[UUID4]):       

        self.SourceMessageId = source_message_id
        self.GroupTraceKey = group_trace_id
     
        return self 