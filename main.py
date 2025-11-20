from fastapi import FastAPI

from app.api.document.document import router as document_router

app = FastAPI(title="MyDocAssistant API", version="0.1.0")

# Include routers
app.include_router(document_router)


@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!"}

