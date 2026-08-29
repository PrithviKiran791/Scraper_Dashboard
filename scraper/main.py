"""
Main entry point for the scraping platform.

Demonstrates the full scraping pipeline:
- Registry-based scraper retrieval
- Fetch pages with HTTPFetcher
- Parse HTML with HTMLParser
- Extract fields with Extractor (configuration-driven)
- Clean data with Cleaner
- Validate with Validator (Pydantic models)
- Export to JSON and CSV
- Report statistics
"""

import logging
from app.scrapers.registry import get_registry, register_scraper, ScraperNotFoundError
from app.scrapers.books_scraper import BooksToScrapeScraper
from app.exporters.json_exporter import JSONExporter
from app.exporters.csv_exporter import CSVExporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    """
    Main function demonstrating the scraping platform.
    
    1. Register available scrapers
    2. Retrieve scraper from registry
    3. Run scraping for 2 pages
    4. Validate records
    5. Display statistics
    6. Export JSON
    7. Export CSV
    """
    
    print("\n" + "="*60)
    print("SCRAPING DASHBOARD - WEB SCRAPING PLATFORM")
    print("="*60)
    
    # Initialize registry and register scrapers
    registry = get_registry()
    
    # Clear previous registrations (for clean state)
    registry.clear()
    
    # Register available scrapers
    logger.info("Registering scrapers...")
    register_scraper(BooksToScrapeScraper)
    
    # Display available scrapers
    print("\nAvailable Scrapers:")
    print("-" * 60)
    
    all_scrapers = registry.list_scrapers()
    for scraper_info in all_scrapers:
        print(
            f"  • {scraper_info['id']:20} | "
            f"{scraper_info['name']:20} | "
            f"{scraper_info['sector']:15} | "
            f"{scraper_info['record_type']}"
        )
    
    if not all_scrapers:
        print("  (No scrapers registered)")
    
    print("\n" + "-" * 60)
    
    # Retrieve scraper from registry
    logger.info("Retrieving BooksToScrape scraper from registry...")
    try:
        scraper = registry.get("books_to_scrape")
        print(f"✓ Retrieved scraper: {scraper.source_name} ({scraper.sector})")
    except ScraperNotFoundError as e:
        logger.error(f"Failed to retrieve scraper: {e}")
        return []
    
    print()
    
    # Run scraping and collect results
    logger.info("Starting scrape job...")
    products = []
    count = 0
    
    for product in scraper.scrape(max_pages=2):
        if product is None:  # Skip invalid products
            continue
        
        count += 1
        products.append(product)
        
        print(
            f"[{count}] {product.name} | "
            f"{product.currency} {product.price} | "
            f"Stock: {product.in_stock}"
        )
    
    print(f"\nSuccessfully processed {count} products\n")
    
    # Display statistics
    if hasattr(scraper, 'stats'):
        scraper.stats.print_stats()
    
    # Export results
    print("Exporting results...\n")
    
    json_path = "output/products.json"
    csv_path = "output/products.csv"
    
    # Export to JSON
    if JSONExporter.export(products, json_path):
        print(f"✓ JSON export: {json_path}")
    else:
        logger.error(f"Failed to export JSON to {json_path}")
    
    # Export to CSV
    if CSVExporter.export(products, csv_path):
        print(f"✓ CSV export: {csv_path}")
    else:
        logger.error(f"Failed to export CSV to {csv_path}")
    
    # Summary statistics
    print(f"\n{'='*60}")
    print("SCRAPING JOB COMPLETED SUCCESSFULLY")
    print(f"{'='*60}\n")
    
    return products


if __name__ == "__main__":
    main()