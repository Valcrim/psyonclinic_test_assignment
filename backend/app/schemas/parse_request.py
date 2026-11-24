from pydantic import BaseModel

class ParseRequest(BaseModel):
    html: str
