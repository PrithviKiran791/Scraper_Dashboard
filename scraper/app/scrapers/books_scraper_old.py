"""
BooksToScrape adapter - concrete implementation using generic components.

This adapter demonstrates how to configure and use the generic scraping engine
for a specific website (BooksToScrape).
"""

from typing import Generator
from urllib.parse import urljoin
from app.core.crawler import Crawler
from app.core.fetcher import HTTPFetcher
from app.models.product import ScrapedProduct
from app.schemas.extraction import ExtractionConfig, ExtractionField
from app.schemas.pagination import URLTemplatePagination


class BooksToScrapeScraper:
    """
    Adapter for scraping BooksToScrape using the generic engine.
    
    This is the first concrete adapter demonstrating how to:
    1. Configure extraction rules
    2. Define pagination strategy
    3. Use the generic crawler
    """
    
    def __init__(self, delay_seconds: float = 1.0):
        """
        Initialize the BooksToScrape adapter.
        
        Args:
            delay_seconds: Delay between requests
        """
        self.source_name = "BooksToScrape"
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
    
    def scrape(self, max_pages: int = 2) -> Generator[ScrapedProduct, None, None]:
        """
        Scrape BooksToScrape and yield ScrapedProduct instances.
        
        Args:
            max_pages: Maximum number of pages to scrape
            
        Yields:
            ScrapedProduct instances
        """
        # Update pagination max_pages
        self.pagination.max_pages = max_pages
        
        # Create crawler
        crawler = Crawler(
            source_name=self.source_name,
            extraction_config=self.extraction_config,
            model=ScrapedProduct,
            pagination=self.pagination,
            fetcher=self.fetcher,
        )
        
        # Crawl and yield records
        for product in crawler.crawl():
            # Post-process product-specific fields
            product = self._postprocess_product(product, crawler.stats.source_url if hasattr(crawler.stats, 'source_url') else "")
            yield product
        
        # Store stats for later access
        self.stats = crawler.get_stats()
        crawler.close()
    
    def _postprocess_product(self, product: ScrapedProduct, page_url: str) -> ScrapedProduct:
        """
        Post-process product after extraction and validation.
        
        Handles:
        - Price parsing from string to Decimal
        - Stock detection from text
        - URL normalization
        
        Args:
            product: ScrapedProduct instance
            page_url: Source page URL
            
        Returns:
            Post-processed ScrapedProduct
        """
        from decimal import Decimal
        from app.core.cleaner import Cleaner
        
        # Parse price if it's still a string
        if isinstance(product.price, str):
            price_decimal = Cleaner.clean_decimal(product.price, Decimal("0.00"))
            if price_decimal and price_decimal > 0:
                product.price = price_decimal
            else:
                # Skip if price is invalid
                return None
        
        # Parse stock status
        if isinstance(product.in_stock, str):
            product.in_stock = Cleaner.clean_boolean(product.in_stock)
        
        # Normalize URLs
        if product.product_url:
            if isinstance(product.product_url, str):
                product.product_url = urljoin("https://books.toscrape.com/catalogue/", product.product_url)
            else:
                product.product_url = str(product.product_url)
        
        if product.image_url:
            if isinstance(product.image_url, str):
                product.image_url = urljoin("https://books.toscrape.com/", product.image_url)
            else:
                product.image_url = str(product.image_url)
        
        # Set category and currency if not set
        if not product.category:
            product.category = "Books"
        if not product.currency:
            product.currency = "GBP"
        
        return product