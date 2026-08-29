"""
Scraper Registry

Centralized registry for managing and retrieving scraper implementations.

Supports:
- Registering scraper classes
- Retrieving scrapers by ID
- Listing available scrapers
- Filtering by sector
"""

import logging
from typing import Dict, List, Optional, Type, Any

logger = logging.getLogger(__name__)


class ScraperNotFoundError(Exception):
    """Raised when a requested scraper is not found in the registry."""
    
    def __init__(self, scraper_id: str):
        self.scraper_id = scraper_id
        super().__init__(f"Scraper not found: '{scraper_id}'")


class DuplicateScraperError(Exception):
    """Raised when attempting to register a scraper that already exists."""
    
    def __init__(self, scraper_id: str):
        self.scraper_id = scraper_id
        super().__init__(f"Scraper '{scraper_id}' is already registered")


class InvalidScraperError(Exception):
    """Raised when attempting to register an invalid scraper."""
    
    def __init__(self, message: str):
        super().__init__(message)


class ScraperRegistry:
    """
    Central registry for scraper implementations.
    
    Provides a single point of access for discovering and instantiating scrapers.
    """
    
    def __init__(self):
        """Initialize an empty registry."""
        self._scrapers: Dict[str, Type] = {}
    
    def register(self, scraper_class: Type, force: bool = False) -> None:
        """
        Register a scraper implementation.
        
        Args:
            scraper_class: The scraper class to register (must inherit from BaseScraper)
            force: If True, overwrite existing registration (default: False)
            
        Raises:
            InvalidScraperError: If scraper_class is invalid
            DuplicateScraperError: If scraper_class is already registered
        """
        from app.scrapers.base import BaseScraper
        
        # Validate scraper class
        if not isinstance(scraper_class, type):
            raise InvalidScraperError(f"Expected a class, got {type(scraper_class)}")
        
        if not issubclass(scraper_class, BaseScraper):
            raise InvalidScraperError(
                f"{scraper_class.__name__} must inherit from BaseScraper"
            )
        
        # Get scraper ID
        scraper_id = scraper_class._get_scraper_id()
        
        # Check for duplicates
        if scraper_id in self._scrapers and not force:
            raise DuplicateScraperError(scraper_id)
        
        # Register
        self._scrapers[scraper_id] = scraper_class
        logger.debug(f"Registered scraper: {scraper_id} ({scraper_class.__name__})")
    
    def get(self, scraper_id: str) -> 'BaseScraper':
        """
        Get a scraper instance by ID.
        
        Args:
            scraper_id: The unique identifier of the scraper (lowercase, snake_case)
            
        Returns:
            An instantiated scraper instance
            
        Raises:
            ScraperNotFoundError: If scraper_id is not found
        """
        if scraper_id not in self._scrapers:
            raise ScraperNotFoundError(scraper_id)
        
        scraper_class = self._scrapers[scraper_id]
        logger.debug(f"Retrieved scraper: {scraper_id}")
        return scraper_class()
    
    def list_scrapers(self, sector: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available scrapers.
        
        Args:
            sector: Optional sector filter (e.g., "ecommerce", "jobs")
            
        Returns:
            List of scraper metadata dictionaries
        """
        scrapers = []
        
        for scraper_id, scraper_class in self._scrapers.items():
            # Create temporary instance to get metadata
            try:
                instance = scraper_class()
                metadata = instance.get_metadata()
                
                # Filter by sector if provided
                if sector and metadata.get('sector') != sector:
                    continue
                
                scrapers.append(metadata)
            except Exception as e:
                logger.warning(f"Failed to get metadata for {scraper_id}: {e}")
                continue
        
        return sorted(scrapers, key=lambda x: x.get('id', ''))
    
    def get_by_source_name(self, source_name: str) -> Optional['BaseScraper']:
        """
        Get a scraper instance by source name.
        
        Args:
            source_name: Human-readable source name (e.g., "BooksToScrape")
            
        Returns:
            Scraper instance or None if not found
        """
        for scraper_id, scraper_class in self._scrapers.items():
            try:
                instance = scraper_class()
                if instance.source_name == source_name:
                    return instance
            except Exception:
                continue
        
        return None
    
    def has_scraper(self, scraper_id: str) -> bool:
        """
        Check if a scraper is registered.
        
        Args:
            scraper_id: The unique identifier of the scraper
            
        Returns:
            True if the scraper is registered, False otherwise
        """
        return scraper_id in self._scrapers
    
    def clear(self) -> None:
        """
        Clear all registered scrapers.
        
        Use with caution - primarily for testing.
        """
        self._scrapers.clear()
        logger.debug("Cleared all registered scrapers")


# Global registry instance
_global_registry = ScraperRegistry()


def get_registry() -> ScraperRegistry:
    """Get the global scraper registry."""
    return _global_registry


def register_scraper(scraper_class: Type, force: bool = False) -> None:
    """
    Convenience function to register a scraper in the global registry.
    
    Args:
        scraper_class: The scraper class to register
        force: If True, overwrite existing registration
    """
    _global_registry.register(scraper_class, force=force)
