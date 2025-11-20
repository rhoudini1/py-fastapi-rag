from datetime import datetime
from typing import Optional

class Document:
    def __init__(
        self,
        id: str,
        filename: str,
        filepath: str,
        uploaded_at: datetime,
        mimetype: Optional[str] = None,
        size: Optional[int] = None,
        description: Optional[str] = None
    ):
        self.id = id
        self.filename = filename
        self.filepath = filepath
        self.uploaded_at = uploaded_at
        self.mimetype = mimetype
        self.size = size
        self.description = description

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "filepath": self.filepath,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "mimetype": self.mimetype,
            "size": self.size,
            "description": self.description,
        }

