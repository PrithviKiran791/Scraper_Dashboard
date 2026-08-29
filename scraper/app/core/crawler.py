"""
Generic Crawler for orchestrating scraping pipeline.

Responsibilities:
- Coordinate fetching
- Parsing
- Extraction
- Pagination
- Delays
- Error handling
- Record collection/yielding
- Statistics
"""

import logging
from typing import Generator, List, Dict, Any, Optional
from datetime import datetime
from app.core.fetcher import HTTPFetcher, FetchResult
from app.core.parser import HTMLParser
from app.core.extractor import Extractor
from app.core.cleaner import Cleaner
from app.core.validator import Validator, ValidationStats
from app.schemas.extraction import ExtractionConfig
from app.schemas.pagination import URLTemplatePagination
from app.models.stats import ScrapingStats
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Crawler:
    """Generic crawler orchestrating the scraping pipeline."""
    
    def __init__(
        self,
        source_name: str,
        extraction_config: ExtractionConfig,
        model: type,
        pagination: URLTemplatePagination,
        fetcher: Optional[HTTPFetcher] = None,
    ):
        """
        Initialize the crawler.
        
        Args:
            source_name: Name of the source being scraped
            extraction_config: Configuration for field extraction
            model: Pydantic model to validate records
            pagination: Pagination strategy
            fetcher: Optional HTTPFetcher (created if not provided)
        """
        self.source_name = source_name
        self.extraction_config = extraction_config
        self.model = model
        self.pagination = pagination
        self.fetcher = fetcher or HTTPFetcher()
        self.extractor = Extractor(extraction_config)
        self.validator = Validator(model)
        self.stats = ScrapingStats(source=source_name)
        self.seen_urls: set = set()  # For deduplication
    
    def crawl(self) -> Generator[BaseModel, None, None]:
        """
        Crawl pages and yield valid records.
        
        Yields:
            Validated model instances
        """
        self.stats.start_time = datetime.now()
        
        for page_num in self.pagination.get_page_range():
            url = self.pagination.get_url(page_num)
            
            # Check for duplicates
            if url in self.seen_urls:
                logger.warning(f"Duplicate URL detected: {url}")
                continue
            
            self.seen_urls.add(url)
            self.stats.pages_requested += 1
            
            # Fetch page
            result = self.fetcher.fetch(url)
            
            if not result.success:
                logger.error(f"Failed to fetch page {page_num}: {result.error}")
                self.stats.pages_failed += 1
                self.stats.failed_pages.append({
                    "url": url,
                    "error": result.error,
                    "page_num": page_num,
                })
                continue
            
            self.stats.pages_fetched += 1
            
            # Parse HTML
            soup = HTMLParser.parse(result.html)
            if not soup:
                logger.error(f"Failed to parse HTML for page {page_num}")
                self.stats.pages_failed += 1
                continue
            
            # Extract records
            raw_records = self.extractor.extract(soup)
            if not raw_records:
                logger.warning(f"No records extracted from page {page_num}")
                continue
            
            # Process each record
            for raw_record in raw_records:
                # Clean record
                cleaned_record = Cleaner.clean_record(raw_record)
                
                # Add source metadata
                cleaned_record['source'] = self.source_name
                cleaned_record['source_url'] = url
                
                self.stats.records_found += 1
                
                # Validate record
                validation_result = self.validator.validate(cleaned_record)
                
                if validation_result.valid:
                    self.stats.records_valid += 1
                    try:
                        instance = self.model(**cleaned_record)
                        yield instance
                    except Exception as e:
                        logger.error(f"Error creating model instance: {str(e)}")
                        self.stats.records_invalid += 1
                else:
                    self.stats.records_invalid += 1
                    logger.warning(f"Record validation failed: {validation_result.errors}")
        
        self.stats.end_time = datetime.now()
        logger.info(f"Crawling completed for {self.source_name}")
    
    def get_stats(self) -> ScrapingStats:
        """Get scraping statistics."""
        return self.stats
    
    def print_stats(self):
        """Print scraping statistics."""
        self.stats.print_stats()
    
    def close(self):
        """Close the crawler and clean up resources."""
        self.fetcher.close()
        logger.info("Crawler closed")
