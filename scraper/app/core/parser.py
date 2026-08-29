"""
Generic HTML Parser using BeautifulSoup.

Responsibilities:
- Convert HTML string to BeautifulSoup object
- Provide parsing utilities
- Keep parsing separate from HTTP fetching
"""

import logging
from typing import Optional
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


class HTMLParser:
    """Generic HTML parser using BeautifulSoup."""
    
    PARSER = "html.parser"  # Can be changed to "lxml", "html5lib", etc.
    
    @staticmethod
    def parse(html: str) -> Optional[BeautifulSoup]:
        """
        Parse HTML string into a BeautifulSoup object.
        
        Args:
            html: HTML string to parse
            
        Returns:
            BeautifulSoup object or None if parsing fails
        """
        if not html or not isinstance(html, str):
            logger.warning("Invalid HTML input")
            return None
        
        try:
            soup = BeautifulSoup(html, HTMLParser.PARSER)
            logger.debug("HTML parsed successfully")
            return soup
        except Exception as e:
            logger.error(f"Failed to parse HTML: {str(e)}")
            return None
    
    @staticmethod
    def select(soup: BeautifulSoup, selector: str) -> list:
        """
        Select multiple elements using CSS selector.
        
        Args:
            soup: BeautifulSoup object
            selector: CSS selector string
            
        Returns:
            List of matching elements
        """
        if not soup or not selector:
            return []
        
        try:
            return soup.select(selector)
        except Exception as e:
            logger.warning(f"Failed to select '{selector}': {str(e)}")
            return []
    
    @staticmethod
    def select_one(soup: BeautifulSoup, selector: str) -> Optional[Tag]:
        """
        Select single element using CSS selector.
        
        Args:
            soup: BeautifulSoup object
            selector: CSS selector string
            
        Returns:
            First matching element or None
        """
        if not soup or not selector:
            return None
        
        try:
            return soup.select_one(selector)
        except Exception as e:
            logger.warning(f"Failed to select '{selector}': {str(e)}")
            return None
    
    @staticmethod
    def get_text(element: Tag, strip: bool = True) -> str:
        """
        Extract text content from an element.
        
        Args:
            element: BeautifulSoup Tag
            strip: Whether to strip whitespace
            
        Returns:
            Text content
        """
        if not element:
            return ""
        
        try:
            return element.get_text(strip=strip)
        except Exception as e:
            logger.warning(f"Failed to extract text: {str(e)}")
            return ""
    
    @staticmethod
    def get_attribute(element: Tag, attr: str, default: Optional[str] = None) -> Optional[str]:
        """
        Extract attribute value from an element.
        
        Args:
            element: BeautifulSoup Tag
            attr: Attribute name
            default: Default value if attribute missing
            
        Returns:
            Attribute value or default
        """
        if not element or not attr:
            return default
        
        try:
            return element.get(attr, default)
        except Exception as e:
            logger.warning(f"Failed to extract attribute '{attr}': {str(e)}")
            return default
