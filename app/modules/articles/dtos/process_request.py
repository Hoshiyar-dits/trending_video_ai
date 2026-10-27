from pydantic import BaseModel

class ProcessRequest(BaseModel):
    publish: bool = False
