from typing import Optional
from pydantic import BaseModel

class DeDuplicationDetails(BaseModel):    
    
    DeDuplicate: bool = None
    UniqueInteractionHeader: Optional[str] = None

    def Create (self, 
               de_duplicate:bool,
               unique_interaction_header:Optional[str]):       

        self.DeDuplicate = de_duplicate
        self.UniqueInteractionHeader = unique_interaction_header
     
        return self 