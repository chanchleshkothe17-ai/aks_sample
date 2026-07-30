from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.db_models import GeneratedImageRecord
from app.models import ImageRecordOut, ImageRequest
from app.services.image_generator import generate_png

router = APIRouter(prefix="/v1", tags=["images"])


@router.post("/images", response_class=Response, summary="Generate a PNG image")
def create_image(request: ImageRequest, db: Session = Depends(get_db)) -> Response:
    image = generate_png(request.prompt, request.width, request.height)
    _upsert_generation_record(db, request)
    return Response(
        content=image,
        media_type="image/png",
        headers={"Content-Disposition": "inline; filename=generated.png"},
    )


def _upsert_generation_record(db: Session, request: ImageRequest) -> None:
    """Fetch any existing row for this prompt and update it; otherwise insert a new one.

    This is the "fetch and update" against Azure SQL — every request either
    creates history or advances an existing record's counters.
    """
    existing = db.execute(
        select(GeneratedImageRecord).where(GeneratedImageRecord.prompt == request.prompt)
    ).scalar_one_or_none()

    if existing is not None:
        existing.request_count += 1
        existing.width = request.width
        existing.height = request.height
    else:
        db.add(
            GeneratedImageRecord(
                prompt=request.prompt,
                width=request.width,
                height=request.height,
            )
        )
    db.commit()


@router.get(
    "/images/history",
    response_model=list[ImageRecordOut],
    summary="List recent generation history from Azure SQL",
)
def list_history(db: Session = Depends(get_db)) -> list[ImageRecordOut]:
    records = (
        db.execute(select(GeneratedImageRecord).order_by(GeneratedImageRecord.updated_at.desc()).limit(50))
        .scalars()
        .all()
    )
    return records
