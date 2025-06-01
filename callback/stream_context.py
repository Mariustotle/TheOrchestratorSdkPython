from orchestrator_sdk.seedworks.logger import Logger
from orchestrator_sdk.contracts.types.crud_action import CrudAction

from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

logger = Logger.get_instance()

class StreamContext(BaseModel):
    action:CrudAction
    event_id:UUID
    stream_identifier:str
    is_latest:bool
    official_created_date:datetime
    effective_from_date:datetime
    effective_to_date:Optional[datetime]

    @staticmethod
    def Create(action:CrudAction, event_id:UUID, stream_identifier:str, is_latest:bool, 
               official_created_date:datetime, effective_from_date:datetime, effective_to_date:Optional[datetime]):
        
        return StreamContext (
            action = action,
            event_id = event_id,
            stream_identifier = stream_identifier,
            is_latest = is_latest,
            official_created_date = official_created_date,
            effective_from_date = effective_from_date,
            effective_to_date = effective_to_date
        )