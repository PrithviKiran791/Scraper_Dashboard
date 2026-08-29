"""
Scrapers package

Provides scraper implementations and registry.
"""

from app.scrapers.base import BaseScraper
from app.scrapers.registry import (
    ScraperRegistry,
    ScraperNotFoundError,
    DuplicateScraperError,
    InvalidScraperError,
    get_registry,
    register_scraper,
)
from app.scrapers.books_scraper import BooksToScrapeScraper

__all__ = [
    "BaseScraper",
    "ScraperRegistry",
    "ScraperNotFoundError",
    "DuplicateScraperError",
    "InvalidScraperError",
    "get_registry",
    "register_scraper",
    "BooksToScrapeScraper",
]
