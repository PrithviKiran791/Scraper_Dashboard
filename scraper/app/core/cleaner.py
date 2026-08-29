"""
Data Cleaner / Normalizer.

Responsibilities:
- whitespace normalization
- HTML entity cleanup
- numeric normalization
- boolean normalization
- currency normalization
- URL normalization
- safe string cleanup
"""

import logging
import re
from decimal import Decimal
from typing import Any, Optional

logger = logging.getLogger(__name__)


class Cleaner:
    """Data cleaner and normalizer."""
    
    @staticmethod
    def clean_string(value: Any, strip: bool = True) -> str:
        """
        Clean and normalize string value.
        
        Args:
            value: Value to clean
            strip: Whether to strip whitespace
            
        Returns:
            Cleaned string
        """
        if value is None:
            return ""
        
        # Convert to string
        text = str(value).strip() if strip else str(value)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    @staticmethod
    def clean_number(value: Any) -> Optional[float]:
        """
        Extract and clean numeric value.
        
        Args:
            value: Value to clean
            
        Returns:
            Numeric value or None
        """
        if value is None:
            return None
        
        # Convert to string
        text = str(value).strip()
        
        # Remove non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', text)
        
        if not cleaned:
            return None
        
        try:
            return float(cleaned)
        except ValueError:
            logger.warning(f"Failed to convert to float: {value}")
            return None
    
    @staticmethod
    def clean_decimal(value: Any, default: Optional[Decimal] = None) -> Optional[Decimal]:
        """
        Extract and clean decimal value.
        
        Args:
            value: Value to clean
            default: Default value if conversion fails
            
        Returns:
            Decimal value or default
        """
        if value is None:
            return default
        
        # Convert to string
        text = str(value).strip()
        
        # Remove non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', text)
        
        if not cleaned:
            return default
        
        try:
            return Decimal(cleaned)
        except Exception as e:
            logger.warning(f"Failed to convert to Decimal: {value} ({str(e)})")
            return default
    
    @staticmethod
    def clean_boolean(value: Any) -> bool:
        """
        Convert value to boolean.
        
        Args:
            value: Value to convert
            
        Returns:
            Boolean value
        """
        if isinstance(value, bool):
            return value
        
        if value is None:
            return False
        
        text = str(value).strip().lower()
        
        # True values
        if text in ('true', 'yes', '1', 'on', 'in stock', 'available'):
            return True
        
        # False values
        return False
    
    @staticmethod
    def clean_currency(value: Any) -> Optional[str]:
        """
        Extract and clean currency code.
        
        Args:
            value: Value to clean
            
        Returns:
            Currency code (3 letters) or None
        """
        if value is None:
            return None
        
        text = str(value).strip().upper()
        
        # Extract currency symbols or codes
        # Common symbols: £, €, $, ¥, ₹, etc.
        currency_map = {
            '£': 'GBP',
            '€': 'EUR',
            '$': 'USD',
            '¥': 'JPY',
            '₹': 'INR',
            'C$': 'CAD',
            'A$': 'AUD',
        }
        
        for symbol, code in currency_map.items():
            if symbol in text:
                return code
        
        # If already a 3-letter code
        if len(text) == 3 and text.isalpha():
            return text
        
        return None
    
    @staticmethod
    def clean_url(value: Any) -> Optional[str]:
        """
        Clean and validate URL.
        
        Args:
            value: Value to clean
            
        Returns:
            URL or None if invalid
        """
        if value is None:
            return None
        
        url = str(value).strip()
        
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            return None
        
        # Remove common URL fragments/parameters that might break parsing
        if '#' in url:
            url = url.split('#')[0]
        
        return url
    
    @staticmethod
    def clean_record(record: dict) -> dict:
        """
        Clean all values in a record dictionary.
        
        Args:
            record: Dictionary to clean
            
        Returns:
            Cleaned dictionary
        """
        cleaned = {}
        
        for key, value in record.items():
            # Skip None values
            if value is None:
                cleaned[key] = None
                continue
            
            # Try to clean strings
            if isinstance(value, str):
                cleaned[key] = Cleaner.clean_string(value)
            else:
                cleaned[key] = value
        
        return cleaned
