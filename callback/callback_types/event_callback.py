
from orchestrator_sdk.contracts.types.activity_type import ActivityTypeEnum
from orchestrator_sdk.contracts.types.message_type import MessageType
from orchestrator_sdk.callback.callback_types.base_callback import BaseCallback
from typing import Literal, Optional
from pydantic import Field

import uuid
from uuid import UUID

class EventCallback(BaseCallback):
    CallbackType: Literal['Events'] 
    JsonPayload:str = None


class EventHeaders():
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
    def Create(message_trace_id_string:str, map_message_id_string:str, message_name:str, application_name:str, dispatcher:str, 
               activity_type_string:str, message_type_string:str, reference:str, priority_string:str, group_trace_key_string:str):        

        priority:int = None
        if (priority_string != None):
            priority = int(priority_string)

        group_trace_key:Optional[UUID] = uuid.UUID(group_trace_key_string) if group_trace_key_string is not None else None
        map_message_id:Optional[UUID] = uuid.UUID(map_message_id_string) if map_message_id_string is not None else None
        message_trace_id:Optional[UUID] = uuid.UUID(message_trace_id_string) if message_trace_id_string is not None else None
        
        activity_type = ActivityTypeEnum[activity_type_string] if activity_type_string != None else None
        message_type = MessageType[message_type_string]

        response = EventHeaders()

        response.message_trace_id = message_trace_id
        response.group_trace_key = group_trace_key
        response.message_name = message_name
        response.application_name = application_name
        response.dispatcher = dispatcher
        response.activity_type = activity_type
        response.message_type = message_type
        response.reference = reference
        response.priority = priority
        response.map_message_id = map_message_id

        return response