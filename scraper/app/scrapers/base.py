import time
import logging
from abc import ABC, abstractmethod
from typing import Generator
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from app.models.product import ScrapedProduct

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class BaseScraper(ABC):
    def __init__(self, source_name: str, base_url: str, delay_seconds: float = 1.0, timeout: int = 10):
        self.source_name = source_name
        self.base_url = base_url
        self.delay_seconds = delay_seconds
        self.timeout = timeout
        self.session = self._init_session()

    def _init_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def fetch_page(self, url: str) -> str:
        try:
            logging.info(f"[{self.source_name}] Fetching: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            time.sleep(self.delay_seconds)
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"[{self.source_name}] Request failed for {url}: {e}")
            return ""

    @abstractmethod
    def scrape(self, max_pages: int = 1) -> Generator[ScrapedProduct, None, None]:
        pass