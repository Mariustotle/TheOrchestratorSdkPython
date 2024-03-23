from pydantic import BaseModel
from typing import Optional

class CommandRaiserRegistration(BaseModel):    
    
    CommandName: str    
    CommandVersion: Optional[str]
    ItemsRemainingAtSource: Optional[int]  

    @staticmethod
    def Create(command_name:str, command_version: Optional[str] = None, items_remaining_at_source:Optional[int] = None):
        
        return CommandRaiserRegistration(
            CommandName=command_name,
            CommandVersion=command_version,
            ItemsRemainingAtSource=items_remaining_at_source)
