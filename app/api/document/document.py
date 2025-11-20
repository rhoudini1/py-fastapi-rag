from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.business.document.save_document import SaveDocumentUseCase
from app.domain.dto.request import UploadDocumentRequest
from app.infra.database import get_db
from app.infra.repositories import DocumentRepository

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)


@router.post("/upload", response_model=dict, summary="Upload a new document")
async def upload_document(
    request: UploadDocumentRequest = Depends(UploadDocumentRequest.as_form),
    session: AsyncSession = Depends(get_db),
):
    try:
        document_repository = DocumentRepository(session)
        save_document_use_case = SaveDocumentUseCase(document_repository)
        
        response = await save_document_use_case.execute(request)
        return JSONResponse(status_code=201, content=response.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

