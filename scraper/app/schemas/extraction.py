"""
Extraction schemas for configuring field extraction.

These schemas define how to extract data from HTML using CSS selectors,
attribute extraction, and default values.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ExtractionField(BaseModel):
    """Configuration for extracting a single field."""
    
    selector: str = Field(..., description="CSS selector to find the element")
    attribute: Optional[str] = Field(None, description="Attribute to extract (if None, extracts text)")
    default: Optional[Any] = Field(None, description="Default value if element not found")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": {
                    "selector": "h3 a",
                    "attribute": "title",
                    "default": "Unknown"
                }
            }
        }


class ExtractionConfig(BaseModel):
    """Configuration for extracting multiple fields from items."""
    
    item_selector: str = Field(..., description="CSS selector to find each item")
    fields: Dict[str, ExtractionField] = Field(..., description="Field extraction configurations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_selector": "article.product_pod",
                "fields": {
                    "name": {
                        "selector": "h3 a",
                        "attribute": "title"
                    },
                    "price": {
                        "selector": "p.price_color"
                    },
                    "stock": {
                        "selector": "p.instock.availability"
                    }
                }
            }
        }
