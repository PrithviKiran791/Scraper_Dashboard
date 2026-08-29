from app.scrapers.books_scraper import BooksToScrapeScraper

def main():
    scraper = BooksToScrapeScraper()
    count = 0
    for product in scraper.scrape(max_pages=2):
        count += 1
        print(f"[{count}] {product.name} | {product.currency} {product.price} | Stock: {product.in_stock}")

if __name__ == "__main__":
    main()