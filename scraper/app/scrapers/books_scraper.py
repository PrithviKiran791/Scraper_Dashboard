"""
BooksToScrape Scraper

Concrete implementation for scraping books.toscrape.com

Demonstrates how to build a scraper using:
1. The generic BaseScraper interface
2. Configuration-driven extraction
3. Domain-specific transformations
"""

import logging
from typing import Generator, Optional, Dict, Any

from urllib.parse import urljoin
from decimal import Decimal
from datetime import datetime

from app.scrapers.base import BaseScraper
from app.core.crawler import Crawler
from app.core.fetcher import HTTPFetcher
from app.core.cleaner import Cleaner
from app.core.parser import HTMLParser
from app.models.product import ScrapedProduct
from app.models.stats import ScrapingStats
from app.schemas.extraction import ExtractionConfig, ExtractionField
from app.schemas.pagination import URLTemplatePagination

logger = logging.getLogger(__name__)


class BooksToScrapeScraper(BaseScraper):
    """
    Scraper for books.toscrape.com
    
    Metadata:
    - source_name: "BooksToScrape"
    - sector: "ecommerce"
    - record_type: "product"
    - base_url: "https://books.toscrape.com"
    """
    
    # Metadata - required by BaseScraper
    source_name = "BooksToScrape"
    sector = "ecommerce"
    record_type = "product"
    base_url = "https://books.toscrape.com"
    
    def __init__(self, delay_seconds: float = 1.0):
        """
        Initialize the BooksToScrape scraper.
        
        Args:
            delay_seconds: Delay between requests for rate limiting
        """
        # Call parent __init__ to validate metadata
        super().__init__()
        
        self.delay_seconds = delay_seconds
        
        # Define extraction configuration
        self.extraction_config = ExtractionConfig(
            item_selector="article.product_pod",
            fields={
                "name": ExtractionField(
                    selector="h3 a",
                    attribute="title",
                ),
                "price": ExtractionField(
                    selector="p.price_color",
                ),
                "in_stock": ExtractionField(
                    selector="p.instock.availability",
                ),
                "product_url": ExtractionField(
                    selector="h3 a",
                    attribute="href",
                ),
                "image_url": ExtractionField(
                    selector="div.image_container img",
                    attribute="src",
                ),
            }
        )
        
        # Define pagination strategy
        self.pagination = URLTemplatePagination(
            template="https://books.toscrape.com/catalogue/page-{}.html",
            start_page=1,
            max_pages=2,
        )
        
        # Create fetcher
        self.fetcher = HTTPFetcher(delay_seconds=delay_seconds)
        self.stats = None
        
        logger.debug(f"Initialized {self.__class__.__name__}")
    
    def scrape(self, max_pages: int = 2) -> Generator[ScrapedProduct, None, None]:
        """
        Scrape BooksToScrape and yield ScrapedProduct instances.
        
        Args:
            max_pages: Maximum number of pages to scrape
            
        Yields:
            ScrapedProduct instances
        """
        logger.info(f"Starting scrape job for {self.source_name} ({max_pages} pages)")
        
        # Update pagination max_pages
        self.pagination.max_pages = max_pages
        
        # Create custom crawler that handles post-processing
        crawler = BooksToScrapeCrawler(
            source_name=self.source_name,
            extraction_config=self.extraction_config,
            model=ScrapedProduct,
            pagination=self.pagination,
            fetcher=self.fetcher,
            base_url=self.base_url,
        )
        
        # Crawl and yield records
        for product in crawler.crawl():
            if product is not None:
                yield product
        
        # Store stats for later access
        self.stats = crawler.get_stats()
        crawler.close()


class BooksToScrapeCrawler(Crawler):
    """Custom crawler for BooksToScrape with domain-specific transformations."""
    
    def __init__(self, base_url: str, **kwargs):
        """Initialize the crawler with base URL for URL resolution."""
        super().__init__(**kwargs)
        self.base_url = base_url
    
    def crawl(self) -> Generator[Optional[ScrapedProduct], None, None]:
        """
        Crawl pages and yield valid records with post-processing.
        
        Yields:
            Validated ScrapedProduct instances
        """
        self.stats.start_time = datetime.now()
        
        for page_num in self.pagination.get_page_range():
            url = self.pagination.get_url(page_num)
            
            # Check for duplicates
            if url in self.seen_urls:
                continue
            
            self.seen_urls.add(url)
            self.stats.pages_requested += 1
            
            # Fetch page
            result = self.fetcher.fetch(url)
            
            if not result.success:
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
                self.stats.pages_failed += 1
                continue
            
            # Extract records
            raw_records = self.extractor.extract(soup)
            
            # Process each record
            for raw_record in raw_records:
                # Clean record
                cleaned_record = Cleaner.clean_record(raw_record)
                
                # Apply domain-specific transformations
                transformed = self._transform_record(cleaned_record, url)
                
                # Add source metadata
                transformed['source'] = self.source_name
                transformed['source_url'] = url
                
                self.stats.records_found += 1
                
                # Validate record
                validation_result = self.validator.validate(transformed)
                
                if validation_result.valid:
                    self.stats.records_valid += 1
                    try:
                        instance = self.model(**transformed)
                        yield instance
                    except Exception as e:
                        self.stats.records_invalid += 1
                else:
                    self.stats.records_invalid += 1
        
        self.stats.end_time = datetime.now()
    
    def _transform_record(self, record: Dict[str, Any], page_url: str) -> Dict[str, Any]:
        """
        Apply domain-specific transformations for BooksToScrape.
        
        Args:
            record: Raw extracted record
            page_url: URL of the page being scraped
            
        Returns:
            Transformed record ready for validation
        """
        # Parse price from string to Decimal
        if 'price' in record and record['price']:
            record['price'] = Cleaner.clean_decimal(record['price'], Decimal("0.00"))
        
        # Parse stock status from text to boolean
        if 'in_stock' in record and record['in_stock']:
            record['in_stock'] = Cleaner.clean_boolean(record['in_stock'])
        
        # Convert relative URLs to absolute
        if 'product_url' in record and record['product_url']:
            record['product_url'] = urljoin(
                f"{self.base_url}/catalogue/",
                record['product_url']
            )
        
        if 'image_url' in record and record['image_url']:
            record['image_url'] = urljoin(
                f"{self.base_url}/",
                record['image_url']
            )
        
        # Set default values
        if 'category' not in record or not record['category']:
            record['category'] = "Books"
        
        if 'currency' not in record or not record['currency']:
            record['currency'] = "GBP"
        
        return record
