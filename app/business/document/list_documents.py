from typing import List

from app.domain.dto.response import ListDocumentsResponse
from app.domain.dto.response.list_documents import DocumentListItem
from app.domain.entities import Document
from app.infra.repositories import DocumentRepository


class ListDocumentsUseCase:
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository

    async def execute(self, page: int = 1, limit: int = 10) -> ListDocumentsResponse:
        documents = await self.document_repository.get_all()
        
        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_documents = documents[start_idx:end_idx]
        
        document_items = [
            DocumentListItem(
                id=doc.id,
                filename=doc.filename,
                uploaded_at=doc.uploaded_at.isoformat() if doc.uploaded_at else "",
                mimetype=doc.mimetype,
                size=doc.size,
                description=doc.description,
            ) for doc in paginated_documents
        ]
        
        return ListDocumentsResponse(
            documents=document_items,
            page=page,
            limit=limit,
        )

