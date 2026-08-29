"""
Generic Extractor for configuration-driven field extraction.

Responsibilities:
- Find elements using CSS selectors
- Extract text by default
- Extract attributes when requested
- Handle missing elements gracefully
- Return raw dictionaries
- Not contain product-specific assumptions
"""

import logging
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup, Tag
from app.schemas.extraction import ExtractionConfig, ExtractionField
from app.core.parser import HTMLParser

logger = logging.getLogger(__name__)


class Extractor:
    """Generic extractor for configuration-driven field extraction."""
    
    def __init__(self, config: ExtractionConfig):
        """
        Initialize the extractor with extraction configuration.
        
        Args:
            config: ExtractionConfig defining how to extract fields
        """
        self.config = config
    
    def extract(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract records from parsed HTML using the configuration.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of dictionaries containing extracted data
        """
        records = []
        
        # Find all items
        items = HTMLParser.select(soup, self.config.item_selector)
        
        if not items:
            logger.warning(f"No items found with selector: {self.config.item_selector}")
            return records
        
        logger.info(f"Found {len(items)} items")
        
        for item in items:
            record = self._extract_record(item)
            if record:
                records.append(record)
        
        logger.info(f"Extracted {len(records)} records")
        return records
    
    def _extract_record(self, item: Tag) -> Optional[Dict[str, Any]]:
        """
        Extract a single record from an item element.
        
        Args:
            item: BeautifulSoup Tag representing a single item
            
        Returns:
            Dictionary of extracted fields or None if extraction fails
        """
        record = {}
        
        for field_name, field_config in self.config.fields.items():
            value = self._extract_field(item, field_config)
            record[field_name] = value
        
        return record if record else None
    
    def _extract_field(self, item: Tag, field_config: ExtractionField) -> Any:
        """
        Extract a single field from an item.
        
        Args:
            item: BeautifulSoup Tag
            field_config: ExtractionField configuration
            
        Returns:
            Extracted value or default value
        """
        # Find the element
        element = HTMLParser.select_one(item, field_config.selector)
        
        if not element:
            logger.debug(f"Element not found for selector: {field_config.selector}")
            return field_config.default
        
        # Extract attribute or text
        if field_config.attribute:
            value = HTMLParser.get_attribute(element, field_config.attribute)
        else:
            value = HTMLParser.get_text(element, strip=True)
        
        # Use default if value is empty
        if not value and field_config.default is not None:
            return field_config.default
        
        return value
