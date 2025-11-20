from fastapi import FastAPI

app = FastAPI(title="MyDocAssistant API", version="0.1.0")


@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!"}

