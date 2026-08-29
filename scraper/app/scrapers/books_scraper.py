import re
from decimal import Decimal
from typing import Generator
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from app.scrapers.base import BaseScraper
from app.models.product import ScrapedProduct

class BooksToScrapeScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            source_name="BooksToScrape",
            base_url="https://books.toscrape.com/catalogue/page-{}.html",
            delay_seconds=1.0
        )

    def _clean_price(self, raw_price: str) -> Decimal:
        cleaned = re.sub(r"[^\d.]", "", raw_price)
        return Decimal(cleaned) if cleaned else Decimal("0.00")

    def scrape(self, max_pages: int = 2) -> Generator[ScrapedProduct, None, None]:
        for page_num in range(1, max_pages + 1):
            url = self.base_url.format(page_num)
            html = self.fetch_page(url)
            if not html:
                break

            soup = BeautifulSoup(html, "html.parser")
            products = soup.select("article.product_pod")
            if not products:
                break

            for product in products:
                title_elem = product.select_one("h3 > a")
                price_elem = product.select_one("p.price_color")
                stock_elem = product.select_one("p.instock.availability")
                img_elem = product.select_one("div.image_container img")

                if not title_elem or not price_elem:
                    continue

                name = title_elem["title"]
                price = self._clean_price(price_elem.get_text(strip=True))
                
                # Skip products with invalid prices
                if price <= 0:
                    continue
                
                in_stock = "In stock" in stock_elem.get_text(strip=True) if stock_elem else False

                product_url = urljoin("https://books.toscrape.com/catalogue/", title_elem["href"])
                image_url = urljoin("https://books.toscrape.com/", img_elem["src"]) if img_elem else None

                yield ScrapedProduct(
                    name=name,
                    price=price,
                    currency="GBP",
                    category="Books",
                    source=self.source_name,
                    product_url=product_url,
                    image_url=image_url,
                    in_stock=in_stock
                )