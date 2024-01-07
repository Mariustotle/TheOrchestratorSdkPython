from typing import Any
from json import loads
from typing import Optional

import json

class ConfigReader:       
    
    
    def convert(self, json_data, class_type):
        if isinstance(json_data, list):
            return [self.convert(item) for item in json_data]
        elif isinstance(json_data, dict):
            instance = class_type()
            for key, value in json_data.items():
                setattr(instance, key, self.convert(value, class_type))
            return instance
        else:
            return json_data
    
    
    def from_json(self, json_payload, class_type):
        
        if isinstance(json_payload, str):
            return json_payload
        
        elif isinstance(json_payload, (dict, list)):
            return  self.convert(json_payload, class_type)
        else:
            raise TypeError("json_data must be a JSON document in str, bytes, bytearray, dict, or list format")       
    
    def __init__(self, file_path:Optional[str] = 'app_config.json'):
        self.file_path = file_path
        with open(file_path, 'r') as file:
            self.config_data = json.load(file)

    def section(self, section_name, data_type):
        if section_name in self.config_data:
            json_data = self.config_data[section_name]            
            return self.from_json(json_data, data_type)       
            
        else:
            raise KeyError(f"Section '{section_name}' not found in the configuration file.")
