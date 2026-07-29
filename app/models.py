from pydantic import BaseModel, Field


class ImageRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=200, examples=["purple mountain sunrise"])
    width: int = Field(default=512, ge=64, le=1024)
    height: int = Field(default=512, ge=64, le=1024)
