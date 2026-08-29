from app.scrapers.books_scraper import BooksToScrapeScraper

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
        count += 1
        print(f"[{count}] {product.name} | {product.currency} {product.price} | Stock: {product.in_stock}")

if __name__ == "__main__":
    main()