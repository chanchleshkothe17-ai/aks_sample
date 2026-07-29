from fastapi import APIRouter
from fastapi.responses import Response

from app.models import ImageRequest
from app.services.image_generator import generate_png

router = APIRouter(prefix="/v1", tags=["images"])


@router.post("/images", response_class=Response, summary="Generate a PNG image")
def create_image(request: ImageRequest) -> Response:
    image = generate_png(request.prompt, request.width, request.height)
    return Response(content=image, media_type="image/png", headers={"Content-Disposition": "inline; filename=generated.png"})
