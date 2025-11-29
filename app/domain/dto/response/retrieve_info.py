from pydantic import BaseModel

class RetrieveInfoResponse(BaseModel):
    message: str
    response: str
