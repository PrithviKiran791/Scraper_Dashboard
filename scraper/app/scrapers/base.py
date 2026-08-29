"""
Generic Scraper Base Class

Provides a common interface and shared infrastructure for all scrapers.

Supports multiple business sectors:
- E-commerce (products)
- Jobs
- Real Estate (properties)
- Companies
- Reviews
"""

import logging
from abc import ABC, abstractmethod
from typing import Generator, TypeVar, Optional, Any

logger = logging.getLogger(__name__)

# Generic type for scraper records
ScrapedRecordType = TypeVar('ScrapedRecordType')


class BaseScraper(ABC):
    """
    Generic base class for all scraper implementations.
    
    Defines the common contract that all scrapers must follow.
    
    Metadata:
    - source_name: Human-readable name of the data source (e.g., "BooksToScrape")
    - sector: Business sector (e.g., "ecommerce", "jobs", "real_estate")
    - record_type: Type of record being scraped (e.g., "product", "job", "property")
    - base_url: Base URL of the source website
    """
    
    # Metadata - MUST be overridden by subclasses
    source_name: str = None
    sector: str = None
    record_type: str = None
    base_url: str = None
    
    def __init__(self):
        """Initialize the scraper."""
        # Validate metadata is defined
        if not self.source_name:
            raise ValueError(f"{self.__class__.__name__} must define 'source_name'")
        if not self.sector:
            raise ValueError(f"{self.__class__.__name__} must define 'sector'")
        if not self.record_type:
            raise ValueError(f"{self.__class__.__name__} must define 'record_type'")
        
        logger.debug(f"Initialized {self.__class__.__name__} "
                    f"[{self.source_name}] ({self.sector})")
    
    @abstractmethod
    def scrape(self, max_pages: int = 1) -> Generator[Any, None, None]:
        """
        Scrape data from the source and yield validated records.
        
        Args:
            max_pages: Maximum number of pages to scrape
            
        Yields:
            Validated record instances (type depends on sector)
            
        Note:
            Subclasses are responsible for:
            - Implementing the scraping logic
            - Yielding validated records
            - Handling pagination
            - Managing statistics
        """
        pass
    
    def get_metadata(self) -> dict:
        """
        Get scraper metadata.
        
        Returns:
            Dictionary with source_name, sector, record_type, and base_url
        """
        return {
            "id": self._get_scraper_id(),
            "name": self.source_name,
            "sector": self.sector,
            "record_type": self.record_type,
            "base_url": self.base_url,
        }
    
    @classmethod
    def _get_scraper_id(cls) -> str:
        """
        Generate a unique scraper identifier from class name.
        
        Format: CamelCase -> snake_case
        Example: BooksToScrapeScraper -> books_to_scrape
        
        Returns:
            Lowercase scraper identifier
        """
        import re
        class_name = cls.__name__
        
        # Remove "Scraper" suffix if present
        if class_name.endswith("Scraper"):
            class_name = class_name[:-7]
        
        # Convert CamelCase to snake_case
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', class_name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()