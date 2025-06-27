from orchestrator_sdk.contracts.types.activity_type import ActivityTypeEnum
from orchestrator_sdk.contracts.types.message_type import MessageType
from orchestrator_sdk.callback.callback_types.base_callback import BaseCallback
from typing import Literal
from pydantic import Field

import uuid

class CommandCallback(BaseCallback):
    CallbackType: Literal['Commands']
    JsonPayload:str = None

class CommandHeaders():
    message_id:uuid = None
    message_trace_id:str = None
    map_message_id:uuid = None
    message_name:str = None
    application_name:str = None
    dispatcher:str = None      
    activity_type:ActivityTypeEnum = None
    message_type:str = None    
    reference:str = None
    priority:int = None

    @staticmethod
    def Create(message_id_string:str, message_trace_id_string:str, map_message_id_string, message_name:str, application_name:str, dispatcher:str, activity_type_string:str, 
               message_type_string:str, reference:str, priority_string:str):
        
        priority:int = None
        if (priority_string != None):
            priority = int(priority_string)

        message_id:uuid = uuid.UUID(message_id_string) if message_id_string is not None else None
        map_message_id:uuid = uuid.UUID(map_message_id_string) if map_message_id_string is not None else None
        activity_type = ActivityTypeEnum[activity_type_string] if activity_type_string != None else None
        message_type = MessageType[message_type_string]

        reponse = CommandHeaders()
        reponse.message_id = message_id
        reponse.message_trace_id = message_trace_id_string
        reponse.map_message_id = map_message_id
        reponse.message_name = message_name
        reponse.application_name = application_name
        reponse.dispatcher = dispatcher
        reponse.activity_type = activity_type
        reponse.message_type = message_type
        reponse.reference = reference
        reponse.priority = priority

        return reponse

