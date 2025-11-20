from fastapi import File, Form, UploadFile
from pydantic import BaseModel, ConfigDict


class UploadDocumentRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    file: UploadFile
    description: str | None = None

    @classmethod
    def as_form(
        cls,
        file: UploadFile = File(...),
        description: str | None = Form(None),
    ):
        return cls(file=file, description=description)
