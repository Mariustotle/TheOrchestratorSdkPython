from orchestrator_sdk.seedworks.logger import Logger
from orchestrator_sdk.contracts.types.data_action import DataActionType

from uuid import UUID
from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel

logger = Logger.get_instance()

class StreamContext(BaseModel):
    event_id:UUID
    stream_segments: Dict[str, str]
    data_action:DataActionType    
    stream_identifier:str
    is_latest:bool
    official_created_date:datetime
    effective_from_date:datetime
    effective_to_date:Optional[datetime]

    @staticmethod
    def Create(data_action:DataActionType, event_id:UUID, stream_identifier:str, is_latest:bool, stream_segments: Dict[str, str],
               official_created_date:datetime, effective_from_date:datetime, effective_to_date:Optional[datetime]):
        
        return StreamContext (
            data_action = data_action,
            event_id = event_id,
            stream_identifier = stream_identifier,
            is_latest = is_latest,
            stream_segments=stream_segments,
            official_created_date = official_created_date,
            effective_from_date = effective_from_date,
            effective_to_date = effective_to_date
        )