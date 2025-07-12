
from typing import Optional


class Logging():    
    file_name:str = None
    path:str = None
    level:str = None
    max_file_size_in_mb: Optional[int] = None
    max_number_of_files: Optional[int] = None
    log_format: Optional[str] = None
