"""
ScrapedCompany model for company/lead intelligence.

Demonstrates the architecture's ability to support multiple business domains.
"""

from typing import Optional
from pydantic import BaseModel, Field, HttpUrl
from app.models.base import ScrapedRecord


class ScrapedCompany(ScrapedRecord):
    """Company information extracted from business intelligence sources."""
    
    company_name: str = Field(..., min_length=1, description="Company name")
    website: Optional[HttpUrl] = Field(None, description="Company website")
    
    industry: Optional[str] = Field(None, description="Industry sector")
    location: Optional[str] = Field(None, description="Company headquarters location")
    description: Optional[str] = Field(None, description="Company description")
    
    employee_count: Optional[int] = Field(None, ge=0, description="Number of employees")
    
    # Contact information where publicly available and legally appropriate
    contact_email: Optional[str] = Field(None, description="Public contact email")
    contact_phone: Optional[str] = Field(None, description="Public phone number")
    
    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "TechCorp Inc",
                "website": "https://techcorp.com",
                "industry": "Software Development",
                "location": "San Francisco, CA",
                "description": "Leading software development company",
                "employee_count": 500,
                "contact_email": "hello@techcorp.com",
                "contact_phone": "+1-555-0100",
                "source": "LinkedIn",
                "source_url": "https://linkedin.com/companies",
            }
        }
