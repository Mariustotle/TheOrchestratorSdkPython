from contextvars import ContextVar
from uuid import UUID
import uuid

class CallbackContext:    
    
    callback_reference: ContextVar[UUID] = ContextVar("callback_reference")
    initialized: ContextVar[bool] = ContextVar("initialized")
    account_id: ContextVar[str] = ContextVar("account_id")
    group_trace_key: ContextVar[str] = ContextVar("group_trace_key")
    message_id: ContextVar[str] = ContextVar("message_id")
    message_name: ContextVar[str] = ContextVar("message_name")
    message_type: ContextVar[str] = ContextVar("message_type")  
    dispatcher: ContextVar[str] = ContextVar("dispatcher")
    reference: ContextVar[str] = ContextVar("reference")
    action: ContextVar[str] = ContextVar("action")
    application_name: ContextVar[str] = ContextVar("application_name")

    def __init__(self, account_id, application_name, message_id, group_trace_key, dispatcher, message_name, message_type, reference, action): 

        self._initialized_token = self.initialized.set(True)        
        self._account_id_token = self.account_id.set(account_id)
        self._application_name_token = self.application_name.set(application_name)
        self._message_id_token = self.message_id.set(message_id)
        self._message_name_token = self.message_name.set(message_name)
        self._message_type_token = self.message_type.set(message_type)
        self._group_trace_key_token = self.group_trace_key.set(group_trace_key)
        self._dispatcher_token = self.dispatcher.set(dispatcher)
        self._reference_token = self.reference.set(reference)
        self._action_token = self.action.set(action)
        self._callback_reference_token = self.callback_reference.set(uuid.uuid4())
        
    def __enter__(self):
        return self
   
    @staticmethod
    def is_available() -> bool:
        
        try: 
            initialized = CallbackContext.initialized.get()
            if initialized is None:
                return False
            else:
                return initialized            
             
        except Exception as ex:
            return False   
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.initialized.reset(self._initialized_token)
        self.account_id.reset(self._account_id_token)
        self.application_name.reset(self._application_name_token)
        self.message_id.reset(self._message_id_token)
        self.message_name.reset(self._message_name_token)
        self.message_type.reset(self._message_type_token)
        self.group_trace_key.reset(self._group_trace_key_token)
        self.dispatcher.reset(self._dispatcher_token)
        self.reference.reset(self._reference_token)
        self.action.reset(self._action_token)
        self.callback_reference.reset(self._callback_reference_token)