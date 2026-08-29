"""
Main entry point for the scraping platform.

Demonstrates the full scraping pipeline:
- Fetch pages with HTTPFetcher
- Parse HTML with HTMLParser
- Extract fields with Extractor (configuration-driven)
- Clean data with Cleaner
- Validate with Validator (Pydantic models)
- Export to JSON and CSV
- Report statistics
"""

import logging
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
    
    1. Initialize BooksToScrape adapter
    2. Run scraping for 2 pages
    3. Validate records
    4. Display statistics
    5. Export JSON
    6. Export CSV
    """
    
    print("\n" + "="*60)
    print("SCRAPING DASHBOARD - WEB SCRAPING PLATFORM")
    print("="*60)
    
    # Initialize scraper
    logger.info("Initializing BooksToScrape scraper...")
    scraper = BooksToScrapeScraper(delay_seconds=1.0)
    
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