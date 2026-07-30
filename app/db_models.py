import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class GeneratedImageRecord(Base):
    """One row per unique prompt this API has ever been asked to render.

    Demonstrates both writes we were asked for: a new prompt inserts a row
    (create), and a repeated prompt updates the existing row's counters
    (fetch + update) instead of just piling up duplicates.
    """

    __tablename__ = "generated_images"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt = Column(String(200), nullable=False, unique=True, index=True)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    request_count = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
