from pydantic import BaseModel
from typing import List, Optional

class DocumentListItem(BaseModel):
    id: str
    filename: str
    uploaded_at: str
    mimetype: Optional[str] = None
    size: Optional[int] = None
    description: Optional[str] = None

class ListDocumentsResponse(BaseModel):
    documents: List[DocumentListItem]
    page: int
    limit: int
