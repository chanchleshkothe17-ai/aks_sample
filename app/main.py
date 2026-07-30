from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database import engine
from app.database import get_db

from app.models import Base
from sqlalchemy import text

from app.schemas import UserCreate
from app.schemas import UserResponse

from app import crud

import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AKS MySQL Sample"
)


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.post(
    "/users",
    response_model=UserResponse
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    return crud.create_user(db, user)


@app.get(
    "/users",
    response_model=list[UserResponse]
)
def users(
    db: Session = Depends(get_db)
):

    return crud.get_users(db)


@app.get(
    "/users/{user_id}",
    response_model=UserResponse
)
def user(
    user_id: int,
    db: Session = Depends(get_db)
):

    db_user = crud.get_user(db, user_id)

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return db_user


@app.delete("/users/{user_id}")
def delete(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = crud.delete_user(db, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "message": "Deleted successfully"
    }
    
@app.get("/ready")
def readiness(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ready"}