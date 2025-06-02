from orchestrator_sdk.contracts.types.action_type import ActionType
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
    message_name:str = None
    application_name:str = None
    dispatcher:str = None      
    action:ActionType = None
    message_type:str = None    
    reference:str = None
    priority:int = None

    @staticmethod
    def Create(message_id_string:str, message_trace_id_string:str, message_name:str, application_name:str, dispatcher:str, action_string:str, 
               message_type_string:str, reference:str, priority_string:str):
        
        priority:int = None
        if (priority_string != None):
            priority = int(priority_string)

        message_id:uuid = uuid.UUID(message_id_string) if message_id_string is not None else None
        action = ActionType[action_string] if action_string != None else None
        message_type = MessageType[message_type_string]

        reponse = CommandHeaders()
        reponse.message_id = message_id
        reponse.message_trace_id = message_trace_id_string
        reponse.message_name = message_name
        reponse.application_name = application_name
        reponse.dispatcher = dispatcher
        reponse.action = action
        reponse.message_type = message_type
        reponse.reference = reference
        reponse.priority = priority

        return reponse

