"""
ScrapedProperty model for real estate analysis.

Demonstrates the architecture's ability to support multiple business domains.
"""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl
from app.models.base import ScrapedRecord


class ScrapedProperty(ScrapedRecord):
    """Real estate property extracted from a property listing site."""
    
    title: str = Field(..., min_length=1, description="Property title/address")
    price: Decimal = Field(..., gt=0, description="Property price")
    currency: str = Field(default="USD", max_length=3, description="Price currency")
    
    location: str = Field(..., min_length=1, description="Property location")
    property_type: Optional[str] = Field(None, description="House, Apartment, Condo, etc.")
    
    bedrooms: Optional[int] = Field(None, ge=0, description="Number of bedrooms")
    bathrooms: Optional[int] = Field(None, ge=0, description="Number of bathrooms")
    area: Optional[Decimal] = Field(None, gt=0, description="Property area (sq ft or sq m)")
    
    property_url: HttpUrl = Field(..., description="URL to the property listing")
    image_url: Optional[HttpUrl] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Beautiful 3-bed house in downtown",
                "price": 500000,
                "currency": "USD",
                "location": "San Francisco, CA",
                "property_type": "House",
                "bedrooms": 3,
                "bathrooms": 2,
                "area": 2500,
                "property_url": "https://example.com/property/123",
                "source": "Zillow",
                "source_url": "https://zillow.com/homes/for_sale",
            }
        }
