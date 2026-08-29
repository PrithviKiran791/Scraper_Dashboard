from datetime import datetime, timezone
from typing import Any, Dict

from pydantic import BaseModel, Field


class ScrapedRecord(BaseModel):
    """
    Generic representation of a record extracted from a website.
    """

    source: str = Field(..., min_length=1)
    source_url: str = Field(..., min_length=1)
    scraped_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    data: Dict[str, Any] = Field(default_factory=dict)