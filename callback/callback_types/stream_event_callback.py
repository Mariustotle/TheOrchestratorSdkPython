from orchestrator_sdk.contracts.types.activity_type import ActivityTypeEnum
from orchestrator_sdk.contracts.types.data_action import DataActionType
from orchestrator_sdk.contracts.types.message_type import MessageType
from orchestrator_sdk.callback.callback_types.base_callback import BaseCallback
from typing import Literal, Dict, Optional
from pydantic import Field

from uuid import UUID
from datetime import datetime

class StreamEventCallback(BaseCallback):
    CallbackType:Literal['StreamOutbound']
    JsonPayload:str = None
    DataAction:DataActionType = None
    EventId:UUID = None
    StreamIdentifier:str = None
    IsLatest:bool = None
    OfficialCreatedDate:datetime = None
    EffectiveFromDate:datetime = None
    EffectiveToDate:Optional[datetime] = None
    StreamSegments: Dict[str, str] = None


class StreamHeaders():
    message_trace_id:Optional[UUID] = None
    map_message_id:Optional[UUID] = None
    group_trace_key:Optional[UUID] = None
    message_name:str = None
    application_name:str = None
    dispatcher:str = None      
    activity_type:ActivityTypeEnum = None
    message_type:str = None    
    reference:str = None
    priority:int = None

    @staticmethod
    def Create(message_trace_id_string:Optional[str], map_message_id_string:Optional[str], message_name:str, application_name:str, dispatcher:str, 
               activity_type_string:str, message_type_string:str, reference:str, priority_string:str, group_trace_key_string:str):        
        
        priority:int = None
        if (priority_string != None):
            priority = int(priority_string)        

        group_trace_key:UUID = UUID(group_trace_key_string) if group_trace_key_string is not None else None
        message_trace_id:UUID = UUID(message_trace_id_string) if message_trace_id_string is not None else None
        map_message_id:UUID = UUID(map_message_id_string) if map_message_id_string is not None else None

        activity_type = ActivityTypeEnum[activity_type_string] if activity_type_string != None else None
        message_type = MessageType[message_type_string]

        reponse = StreamHeaders()
        reponse.group_trace_key = group_trace_key
        reponse.message_trace_id = message_trace_id
        reponse.map_message_id = map_message_id
        reponse.message_name = message_name
        reponse.application_name = application_name
        reponse.dispatcher = dispatcher
        reponse.activity_type = activity_type
        reponse.message_type = message_type
        reponse.reference = reference
        reponse.priority = priority

        return reponse