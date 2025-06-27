import uuid

class HeaderProperties:
    callback_reference: uuid = None
    account_id: str = None
    group_trace_key: str = None
    message_id: str = None
    trace_message_id: str = None
    map_message_id: str = None
    message_name: str = None
    message_type: str = None
    process_structure: str = None
    dispatcher: str = None
    reference: str = None
    activity_type: str = None
    application_name: str = None
    priority: str = None

    def __init__(self, account_id, application_name, message_id, trace_message_id, map_message_id, group_trace_key, dispatcher, message_name, message_type, process_structure, reference, activity_type, priority = None): 
        self.callback_reference = uuid.uuid4()
        self.account_id = account_id
        self.application_name = application_name
        self.trace_message_id = trace_message_id
        self.map_message_id = map_message_id
        self.message_name = message_name
        self.message_id = message_id
        self.message_type = message_type
        self.process_structure = process_structure
        self.group_trace_key = group_trace_key
        self.dispatcher = dispatcher
        self.reference = reference
        self.activity_type = activity_type
        self.priority = priority

