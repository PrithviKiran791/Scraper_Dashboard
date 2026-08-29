"""
ScrapedReview model for market research and reviews.

Demonstrates the architecture's ability to support multiple business domains.
"""

from typing import Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from app.models.base import ScrapedRecord


class ScrapedReview(ScrapedRecord):
    """Product or service review extracted from review sites."""
    
    product: str = Field(..., min_length=1, description="Product or service name")
    rating: Optional[Decimal] = Field(None, ge=0, le=5, description="Review rating (0-5)")
    
    review_title: Optional[str] = Field(None, description="Review title/headline")
    review_text: Optional[str] = Field(None, description="Review body text")
    
    author: Optional[str] = Field(None, description="Review author/reviewer name")
    published_date: Optional[datetime] = None
    
    source_url: str = Field(..., min_length=1, description="URL where review was found")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product": "Amazing Product X",
                "rating": 4.5,
                "review_title": "Great product, highly recommend",
                "review_text": "This product exceeded my expectations...",
                "author": "John Doe",
                "published_date": "2026-08-29T00:00:00Z",
                "source": "Amazon",
                "source_url": "https://amazon.com/product/reviews/123",
            }
        }
