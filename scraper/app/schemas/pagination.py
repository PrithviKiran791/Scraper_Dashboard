"""
Pagination schemas for different pagination strategies.

Supports:
- URL template pagination (e.g., page-1, page-2)
- Next-link pagination (architecture support for future)
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class URLTemplatePagination(BaseModel):
    """
    URL template-based pagination.
    
    Example:
        template: "https://example.com/page-{}.html"
        start_page: 1
        max_pages: 5
    """
    
    template: str = Field(..., description="URL template with {} placeholder for page number")
    start_page: int = Field(default=1, description="Starting page number")
    max_pages: int = Field(default=1, description="Maximum number of pages to scrape")
    
    def get_url(self, page_num: int) -> str:
        """Get URL for a specific page number."""
        return self.template.format(page_num)
    
    def get_page_range(self) -> range:
        """Get range of page numbers to iterate."""
        return range(self.start_page, self.start_page + self.max_pages)


class NextLinkPagination(BaseModel):
    """
    Next-link based pagination (for future implementation).
    
    Supports extracting "next" link from page and following it.
    """
    
    next_selector: str = Field(..., description="CSS selector for next page link")
    next_attribute: str = Field(default="href", description="Attribute to extract URL from")
    max_pages: int = Field(default=1, description="Maximum number of pages to scrape")
    
    class Config:
        json_schema_extra = {
            "example": {
                "next_selector": "a.next",
                "next_attribute": "href",
                "max_pages": 10
            }
        }


class PaginationStrategy(BaseModel):
    """
    Base configuration for pagination strategy selection.
    
    Can specify one of:
    - url_template: For sequential URL patterns
    - next_link: For following next/previous links
    """
    
    strategy_type: str = Field("url_template", description="Type of pagination: 'url_template' or 'next_link'")
    url_template: Optional[URLTemplatePagination] = None
    next_link: Optional[NextLinkPagination] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "strategy_type": "url_template",
                "url_template": {
                    "template": "https://example.com/page-{}.html",
                    "start_page": 1,
                    "max_pages": 5
                }
            }
        }
