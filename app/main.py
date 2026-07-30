from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import router
from app.db import engine
from app.db_models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Creates the table on startup if it doesn't exist yet. For a real production
    # rollout you'd move this to a proper migration tool (Alembic) instead —
    # fine for getting this running end-to-end first.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Image Generator API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "Welcome to Image Generator API",
        "status": "Running",
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }
