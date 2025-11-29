from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.business.document.save_document import SaveDocumentUseCase
from app.business.document.list_documents import ListDocumentsUseCase
from app.business.talk.retrieve_info import RetrieveInfoUseCase
from app.domain.dto.request import RetrieveInfoRequest, UploadDocumentRequest
from app.infra.database import get_db
from app.infra.gateway import GeminiGateway
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
        gemini_gateway = GeminiGateway()
        save_document_use_case = SaveDocumentUseCase(document_repository, gemini_gateway)
        
        response = await save_document_use_case.execute(request)
        return JSONResponse(status_code=201, content=response.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/talk", response_model=dict, summary="Talk to the documents")
async def retrieve(
    request: RetrieveInfoRequest,
):
    try:
        gemini_gateway = GeminiGateway()
        retrieve_info_use_case = RetrieveInfoUseCase(gemini_gateway)

        response = await retrieve_info_use_case.execute(message=request.message)

        return JSONResponse(status_code=201, content=response.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieve failed: {str(e)}")


@router.get("/", summary="List all uploaded documents")
async def list_documents(
    page: int = 1,
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
):
    try:
        if page < 1:
            raise HTTPException(status_code=400, detail="page must be >= 1")
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="limit must be between 1 and 100")
        
        document_repository = DocumentRepository(session)
        list_documents_use_case = ListDocumentsUseCase(document_repository)
        
        response = await list_documents_use_case.execute(page=page, limit=limit)
        return JSONResponse(status_code=200, content=response.model_dump())

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")
