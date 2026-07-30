from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ImageRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=200, examples=["purple mountain sunrise"])
    width: int = Field(default=512, ge=64, le=1024)
    height: int = Field(default=512, ge=64, le=1024)


class ImageRecordOut(BaseModel):
    """What we hand back when reading generation history out of Azure SQL."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    prompt: str
    width: int
    height: int
    request_count: int
    created_at: datetime
    updated_at: datetime
