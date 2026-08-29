"""
ScrapedJob model for job market analysis.

Demonstrates the architecture's ability to support multiple business domains.
"""

from decimal import Decimal
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from app.models.base import ScrapedRecord


class ScrapedJob(ScrapedRecord):
    """Job posting extracted from a job board."""
    
    title: str = Field(..., min_length=1, description="Job title")
    company: str = Field(..., min_length=1, description="Company name")
    location: str = Field(..., min_length=1, description="Job location")
    
    salary: Optional[Decimal] = Field(None, ge=0, description="Salary amount")
    salary_currency: Optional[str] = Field(default="USD", max_length=3, description="Salary currency")
    
    employment_type: Optional[str] = Field(None, description="Full-time, Part-time, Contract, etc.")
    skills: Optional[list] = Field(default_factory=list, description="Required skills")
    
    posted_date: Optional[datetime] = None
    job_url: HttpUrl = Field(..., description="URL to the job posting")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Senior Python Developer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
                "salary": 150000,
                "salary_currency": "USD",
                "employment_type": "Full-time",
                "skills": ["Python", "FastAPI", "PostgreSQL"],
                "job_url": "https://example.com/jobs/123",
                "source": "LinkedIn",
                "source_url": "https://linkedin.com/jobs/search",
                "posted_date": "2026-08-29T00:00:00Z",
            }
        }
