from functools import wraps
from fastapi import Request

from orchestrator_sdk.callback_context import CallbackContext

def init_callback_context_for_fastapi(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")
        
        if request:            
            # From HTTP Header
            account_id = request.headers.get("AccountId")
            
            # From Query String
            reference = request.query_params.get("Reference")
            message_id = request.query_params.get("MessageId")
            message_name = request.query_params.get("MessageName")
            message_type = request.query_params.get("MessageType")       
            group_trace_key = request.query_params.get("GroupTraceKey")
            dispatcher = request.query_params.get("Dispatcher")
            action_type = request.query_params.get("ActionType")
            
            with CallbackContext(
                account_id=account_id,
                message_id=message_id,
                group_trace_key=group_trace_key,
                dispatcher=dispatcher,
                message_name=message_name,
                message_type = message_type,
                reference=reference,
                action_type=action_type):             
                
                return await func(*args, **kwargs)
        else:
            return await func(*args, **kwargs)
        
    return wrapper
