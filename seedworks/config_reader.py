from typing import Any, Optional, get_args, get_origin, Union
import json


class ConfigReader:
    def __init__(self, file_path: Optional[str] = 'app_config.json'):
        self.file_path = file_path
        with open(file_path, 'r') as file:
            self.config_data = json.load(file)

    def _resolve_type(self, annotation):
        """
        Resolve Optional[T] -> T
        Resolve plain T -> T
        """
        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin is Union:
            non_none = [a for a in args if a is not type(None)]
            if len(non_none) == 1:
                return non_none[0]

        return annotation

    def _is_primitive_type(self, t) -> bool:
        return t in (str, int, float, bool, Any)

    def _convert_value(self, value, target_type):
        """
        Convert a raw JSON value into the requested target type.
        """
        if target_type is None or target_type is Any:
            return value

        target_type = self._resolve_type(target_type)
        origin = get_origin(target_type)
        args = get_args(target_type)

        if value is None:
            return None

        # Handle list[T]
        if origin is list:
            item_type = args[0] if args else Any
            if not isinstance(value, list):
                raise TypeError(f"Expected list for {target_type}, got {type(value).__name__}")
            return [self._convert_value(item, item_type) for item in value]

        # Handle primitive values
        if self._is_primitive_type(target_type):
            try:
                if target_type is Any:
                    return value
                return target_type(value)
            except Exception:
                return value

        # Handle nested object
        if isinstance(value, dict):
            return self._convert_object(value, target_type)

        # Fallback
        return value

    def _convert_object(self, json_data: dict, class_type):
        """
        Create an instance of class_type and apply only values present in json_data.
        Missing values remain at their class defaults.
        """
        instance = class_type()

        annotations = getattr(class_type, '__annotations__', {})

        for key, value in json_data.items():
            target_attr_type = annotations.get(key, Any)
            converted_value = self._convert_value(value, target_attr_type)
            setattr(instance, key, converted_value)

        return instance

    def from_json(self, json_payload, class_type):
        if isinstance(json_payload, str):
            # If caller asked for str, return as-is
            if class_type is str:
                return json_payload

            # Otherwise interpret it as raw JSON text
            json_payload = json.loads(json_payload)

        if isinstance(json_payload, dict):
            return self._convert_object(json_payload, class_type)

        if isinstance(json_payload, list):
            origin = get_origin(class_type)
            args = get_args(class_type)

            if origin is list:
                item_type = args[0] if args else Any
                return [self._convert_value(item, item_type) for item in json_payload]

            return json_payload

        raise TypeError(
            "json_payload must be a JSON string, dict, or list"
        )

    def section(self, section_name, data_type):
        """
        Returns the config section converted to data_type.
        If the section does not exist, returns a default instance of data_type.
        """
        if section_name in self.config_data:
            json_data = self.config_data[section_name]
            return self.from_json(json_data, data_type)

        # Default fallback when section missing
        return data_type()