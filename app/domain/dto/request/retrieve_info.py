from pydantic import BaseModel


class RetrieveInfoRequest(BaseModel):
    message: str
