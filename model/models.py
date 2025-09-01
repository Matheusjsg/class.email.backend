from pydantic import BaseModel

class EmailText(BaseModel):
    text: str
