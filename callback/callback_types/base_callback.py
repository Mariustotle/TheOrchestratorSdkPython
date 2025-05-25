from pydantic import BaseModel

class BaseCallback(BaseModel):
    CallbackType: str