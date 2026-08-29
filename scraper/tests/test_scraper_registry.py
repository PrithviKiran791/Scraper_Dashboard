"""
Tests for the Scraper Registry

Test cases:
1. BooksToScrape is registered
2. Registry can retrieve BooksToScrape
3. Retrieved instance is a BooksToScrapeScraper
4. Registry returns correct metadata
5. list_scrapers() returns BooksToScrape
6. list_scrapers(sector="ecommerce") returns BooksToScrape
7. list_scrapers(sector="jobs") returns empty list
8. Requesting unknown scraper raises clear exception
9. BooksToScrape scraper still works after refactor
"""

import pytest
import sys
from pathlib import Path

# Add scraper module to path
scraper_path = Path(__file__).parent.parent / "scraper"
if str(scraper_path) not in sys.path:
    sys.path.insert(0, str(scraper_path))

from app.scrapers.registry import (
    ScraperRegistry,
    ScraperNotFoundError,
    DuplicateScraperError,
    InvalidScraperError,
    get_registry,
    register_scraper,
)
from app.scrapers.books_scraper import BooksToScrapeScraper
from app.scrapers.base import BaseScraper


class TestScraperRegistry:
    """Test suite for ScraperRegistry"""
    
    @pytest.fixture
    def registry(self):
        """Create a fresh registry for each test"""
        registry = ScraperRegistry()
        return registry
    
    def test_1_books_to_scrape_can_be_registered(self, registry):
        """Test 1: BooksToScrape can be registered"""
        # Should not raise any exception
        registry.register(BooksToScrapeScraper)
        
        # Verify it was registered
        assert registry.has_scraper("books_to_scrape")
    
    def test_2_retrieve_books_to_scrape(self, registry):
        """Test 2: Registry can retrieve BooksToScrape"""
        registry.register(BooksToScrapeScraper)
        
        # Retrieve the scraper
        scraper = registry.get("books_to_scrape")
        
        # Should not be None
        assert scraper is not None
    
    def test_3_retrieved_instance_type(self, registry):
        """Test 3: Retrieved instance is a BooksToScrapeScraper"""
        registry.register(BooksToScrapeScraper)
        
        scraper = registry.get("books_to_scrape")
        
        # Check type
        assert isinstance(scraper, BooksToScrapeScraper)
        assert isinstance(scraper, BaseScraper)
    
    def test_4_metadata_is_correct(self, registry):
        """Test 4: Registry returns correct metadata"""
        registry.register(BooksToScrapeScraper)
        
        scraper = registry.get("books_to_scrape")
        metadata = scraper.get_metadata()
        
        # Verify metadata
        assert metadata["id"] == "books_to_scrape"
        assert metadata["name"] == "BooksToScrape"
        assert metadata["sector"] == "ecommerce"
        assert metadata["record_type"] == "product"
        assert metadata["base_url"] == "https://books.toscrape.com"
    
    def test_5_list_scrapers_includes_books_to_scrape(self, registry):
        """Test 5: list_scrapers() returns BooksToScrape"""
        registry.register(BooksToScrapeScraper)
        
        scrapers = registry.list_scrapers()
        
        # Should have at least one scraper
        assert len(scrapers) >= 1
        
        # Find BooksToScrape
        books_scraper = next(
            (s for s in scrapers if s["id"] == "books_to_scrape"),
            None
        )
        assert books_scraper is not None
        assert books_scraper["name"] == "BooksToScrape"
    
    def test_6_filter_by_sector_ecommerce(self, registry):
        """Test 6: list_scrapers(sector="ecommerce") returns BooksToScrape"""
        registry.register(BooksToScrapeScraper)
        
        scrapers = registry.list_scrapers(sector="ecommerce")
        
        # Should have BooksToScrape
        assert len(scrapers) >= 1
        
        books_scraper = next(
            (s for s in scrapers if s["id"] == "books_to_scrape"),
            None
        )
        assert books_scraper is not None
    
    def test_7_filter_by_sector_jobs_empty(self, registry):
        """Test 7: list_scrapers(sector="jobs") returns empty list"""
        registry.register(BooksToScrapeScraper)
        
        scrapers = registry.list_scrapers(sector="jobs")
        
        # Should be empty for jobs sector
        assert len(scrapers) == 0
    
    def test_8_unknown_scraper_raises_error(self, registry):
        """Test 8: Requesting unknown scraper raises clear exception"""
        registry.register(BooksToScrapeScraper)
        
        # Try to get a non-existent scraper
        with pytest.raises(ScraperNotFoundError) as exc_info:
            registry.get("non_existent_scraper")
        
        # Error should contain the scraper ID
        assert "non_existent_scraper" in str(exc_info.value)
    
    def test_duplicate_registration_raises_error(self, registry):
        """Test: Duplicate registration raises DuplicateScraperError"""
        registry.register(BooksToScrapeScraper)
        
        # Try to register the same scraper again
        with pytest.raises(DuplicateScraperError):
            registry.register(BooksToScrapeScraper)
    
    def test_force_registration_overwrites(self, registry):
        """Test: Force registration overwrites existing"""
        registry.register(BooksToScrapeScraper)
        
        # Force register again
        registry.register(BooksToScrapeScraper, force=True)
        
        # Should still be retrievable
        scraper = registry.get("books_to_scrape")
        assert scraper is not None
    
    def test_invalid_scraper_class_raises_error(self, registry):
        """Test: Registering non-BaseScraper class raises error"""
        
        class NotAScraper:
            pass
        
        with pytest.raises(InvalidScraperError):
            registry.register(NotAScraper)
    
    def test_invalid_scraper_id_raises_error(self, registry):
        """Test: Registering non-class raises InvalidScraperError"""
        
        with pytest.raises(InvalidScraperError):
            registry.register("not_a_class")
    
    def test_has_scraper_returns_bool(self, registry):
        """Test: has_scraper returns correct boolean"""
        registry.register(BooksToScrapeScraper)
        
        assert registry.has_scraper("books_to_scrape") is True
        assert registry.has_scraper("non_existent") is False
    
    def test_get_by_source_name(self, registry):
        """Test: get_by_source_name retrieves scraper"""
        registry.register(BooksToScrapeScraper)
        
        scraper = registry.get_by_source_name("BooksToScrape")
        
        assert scraper is not None
        assert scraper.source_name == "BooksToScrape"
    
    def test_get_by_source_name_not_found(self, registry):
        """Test: get_by_source_name returns None for unknown"""
        registry.register(BooksToScrapeScraper)
        
        scraper = registry.get_by_source_name("UnknownSource")
        
        assert scraper is None


class TestGlobalRegistry:
    """Test suite for global registry functions"""
    
    def test_get_registry_returns_singleton(self):
        """Test: get_registry returns the same instance"""
        reg1 = get_registry()
        reg2 = get_registry()
        
        assert reg1 is reg2
    
    def test_register_scraper_function(self):
        """Test: register_scraper convenience function works"""
        registry = get_registry()
        registry.clear()
        
        # Use convenience function
        register_scraper(BooksToScrapeScraper)
        
        # Verify it was registered
        assert registry.has_scraper("books_to_scrape")


class TestBooksToScraperMetadata:
    """Test suite for BooksToScrapeScraper metadata"""
    
    def test_source_name_is_defined(self):
        """Test: BooksToScrapeScraper.source_name is defined"""
        scraper = BooksToScrapeScraper()
        assert scraper.source_name == "BooksToScrape"
    
    def test_sector_is_defined(self):
        """Test: BooksToScrapeScraper.sector is defined"""
        scraper = BooksToScrapeScraper()
        assert scraper.sector == "ecommerce"
    
    def test_record_type_is_defined(self):
        """Test: BooksToScrapeScraper.record_type is defined"""
        scraper = BooksToScrapeScraper()
        assert scraper.record_type == "product"
    
    def test_base_url_is_defined(self):
        """Test: BooksToScrapeScraper.base_url is defined"""
        scraper = BooksToScrapeScraper()
        assert scraper.base_url == "https://books.toscrape.com"
    
    def test_scraper_id_generation(self):
        """Test: Scraper ID is generated correctly"""
        scraper_id = BooksToScrapeScraper._get_scraper_id()
        assert scraper_id == "books_to_scrape"


class TestBooksToScraperFunctionality:
    """Test suite for BooksToScrapeScraper core functionality"""
    
    def test_9_scraper_can_scrape_without_internet(self):
        """Test 9: BooksToScrape scraper is properly initialized"""
        # This test verifies the scraper can be instantiated and configured
        # Full integration test requires internet access
        
        scraper = BooksToScrapeScraper(delay_seconds=1.0)
        
        # Verify scraper attributes
        assert scraper.source_name == "BooksToScrape"
        assert scraper.sector == "ecommerce"
        assert scraper.record_type == "product"
        assert scraper.base_url == "https://books.toscrape.com"
        assert scraper.extraction_config is not None
        assert scraper.pagination is not None
        assert scraper.fetcher is not None
    
    def test_scraper_inherits_from_base_scraper(self):
        """Test: BooksToScrapeScraper properly inherits from BaseScraper"""
        scraper = BooksToScrapeScraper()
        
        # Should be instance of BaseScraper
        assert isinstance(scraper, BaseScraper)
        
        # Should have scrape method
        assert hasattr(scraper, 'scrape')
        assert callable(scraper.scrape)
    
    def test_scraper_has_get_metadata_method(self):
        """Test: BooksToScrapeScraper has get_metadata method"""
        scraper = BooksToScrapeScraper()
        
        metadata = scraper.get_metadata()
        
        # Metadata should be a dict with expected keys
        assert isinstance(metadata, dict)
        assert 'id' in metadata
        assert 'name' in metadata
        assert 'sector' in metadata
        assert 'record_type' in metadata


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
