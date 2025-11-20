from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.types import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.database import Base
from app.domain.entities import Document

# SQLAlchemy model
class DocumentModel(Base):
    """SQLAlchemy model for Document entity."""
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(nullable=False)
    filepath: Mapped[str] = mapped_column(nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    mimetype: Mapped[Optional[str]] = mapped_column(nullable=True)
    size: Mapped[Optional[int]] = mapped_column(nullable=True)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)


class DocumentRepository:
    """Repository for Document CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, document: Document) -> Document:
        """Save a new document to the database."""
        document_model = DocumentModel(
            id=document.id,
            filename=document.filename,
            filepath=document.filepath,
            uploaded_at=document.uploaded_at,
            mimetype=document.mimetype,
            size=document.size,
            description=document.description,
        )
        self.session.add(document_model)
        await self.session.commit()
        await self.session.refresh(document_model)
        return self._model_to_entity(document_model)

    async def get_by_id(self, document_id: str) -> Optional[Document]:
        """Retrieve a document by its ID."""
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.id == document_id)
        )
        document_model = result.scalar_one_or_none()
        if document_model:
            return self._model_to_entity(document_model)
        return None

    async def get_all(self) -> List[Document]:
        """Retrieve all documents."""
        result = await self.session.execute(select(DocumentModel))
        document_models = result.scalars().all()
        return [self._model_to_entity(model) for model in document_models]

    async def update(self, document: Document) -> Optional[Document]:
        """Update an existing document."""
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.id == document.id)
        )
        document_model = result.scalar_one_or_none()
        if not document_model:
            return None

        document_model.filename = document.filename
        document_model.filepath = document.filepath
        document_model.uploaded_at = document.uploaded_at
        document_model.mimetype = document.mimetype
        document_model.size = document.size
        document_model.description = document.description

        await self.session.commit()
        await self.session.refresh(document_model)
        return self._model_to_entity(document_model)

    async def delete(self, document_id: str) -> bool:
        """Delete a document by its ID."""
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.id == document_id)
        )
        document_model = result.scalar_one_or_none()
        if not document_model:
            return False

        await self.session.delete(document_model)
        await self.session.commit()
        return True

    @staticmethod
    def _model_to_entity(model: DocumentModel) -> Document:
        """Convert SQLAlchemy model to domain entity."""
        return Document(
            id=model.id,
            filename=model.filename,
            filepath=model.filepath,
            uploaded_at=model.uploaded_at,
            mimetype=model.mimetype,
            size=model.size,
            description=model.description,
        )

