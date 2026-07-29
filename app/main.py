from fastapi import FastAPI

from app.api import router

app = FastAPI(
    title="Image Generator API",
    version="1.0.0"
)

app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "Welcome to Image Generator API",
        "status": "Running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }