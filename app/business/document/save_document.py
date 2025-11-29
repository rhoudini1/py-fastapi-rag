from datetime import datetime, timezone
import os
import uuid

from app.domain.dto.request import UploadDocumentRequest
from app.domain.dto.response import UploadDocumentResponse
from app.domain.entities import Document
from app.infra.gateway import GeminiGateway
from app.infra.repositories import DocumentRepository


class SaveDocumentUseCase:
    def __init__(self,
        document_repository: DocumentRepository,
        gemini_gateway: GeminiGateway,
        upload_dir: str = "uploaded_files"
        ):
        self.document_repository = document_repository
        self.gemini_gateway = gemini_gateway
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    async def execute(self, request: UploadDocumentRequest) -> UploadDocumentResponse:
        file = request.file
        description = request.description

        doc_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename or "")[1]
        stored_filename = f"{doc_id}{file_ext}" if file_ext else doc_id
        filepath = os.path.join(self.upload_dir, stored_filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        file_bytes = await file.read()
        with open(filepath, "wb") as buffer:
            buffer.write(file_bytes)

        size = os.path.getsize(filepath)

        document = Document(
            id=doc_id,
            filename=file.filename,
            filepath=filepath,
            uploaded_at=datetime.now(timezone.utc),
            mimetype=file.content_type,
            size=size,
            description=description,
        )

        # Save document to database using repository
        saved_document = await self.document_repository.create(document)

        # Index document using Gemini gateway
        self.gemini_gateway.index_document(saved_document)

        return UploadDocumentResponse(
            id=saved_document.id,
            filename=saved_document.filename,
            filepath=saved_document.filepath,
        )
