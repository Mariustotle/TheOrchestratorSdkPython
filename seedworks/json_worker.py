import json
import dataclasses, inspect, json
from orchestrator_sdk.seedworks.logger import Logger

logger = Logger.get_instance()

def _default_serialiser(o): #this serialiser is for 'Object of type UUID is not JSON seralisable' exceptions, and general consistent serialisation.
    return str(o)

class JsonWorker:

    def read_as_json(self, raw_payload):
        try:
            if isinstance(raw_payload, (dict, list)):
                return json.loads(json.dumps(raw_payload, default=_default_serialiser))

            if raw_payload is None:
                raise ValueError("Empty JSON payload (None), cannot convert.")

            if isinstance(raw_payload, str):
                raw_payload = raw_payload.strip()
                if raw_payload == "":
                    raise ValueError("Empty JSON payload (Empty.String), cannot convert.")
                return json.loads(raw_payload)

            # NEW: handle dataclass or any object with __dict__
            if dataclasses.is_dataclass(raw_payload):
                return json.loads(json.dumps(dataclasses.asdict(raw_payload), default=_default_serialiser))

            if hasattr(raw_payload, "__dict__"):
                return json.loads(json.dumps(raw_payload.__dict__, default=_default_serialiser))

            # Optionally still handle raw *classes* (rarely useful)
            if inspect.isclass(raw_payload):
                return json.loads(json.dumps(raw_payload, default=lambda o: o.__dict__))

            raise TypeError(f"Cannot read as JSON, unknown data type [{type(raw_payload)}].")

        except Exception as ex:
            logger.error(f"Failed to read payload as JSON [{raw_payload}]. Details:[{ex}]")
            raise


    def convert_json_to_class(self, json_content, class_type):
        try:
             
            if (not isinstance(json_content, (dict, list))):
                raise Exception(f"Please read as json before attempting to cast to class instance.")
            
            if (class_type is None):
                raise Exception(f"Cannot cast JSON [{json_content}] to class as no class type was provided.")
            
            if not inspect.isclass(class_type):
                raise TypeError(
                    f"To cast JSON [{json_content}] into a class you need to provide a valid class type. Provided: {type(class_type).__name__}"
                )

            return class_type.parse_obj(json_content)

        except Exception as ex:
            logger.error(f"Failed to convert JSON payload [{json_content}] into [{class_type}]. Details: [{str(ex)}]")
            raise