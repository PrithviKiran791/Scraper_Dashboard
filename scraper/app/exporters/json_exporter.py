"""
JSON Exporter for saving scraping results.

Responsibilities:
- Write UTF-8 JSON
- Preserve Unicode
- Support lists of Pydantic models
- Serialize Decimal correctly
- Serialize datetime correctly
"""

import json
import logging
from typing import List, Any, Dict
from decimal import Decimal
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for Decimal, datetime, and Pydantic URL objects."""
    
    def default(self, obj: Any) -> Any:
        """Handle special types."""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, BaseModel):
            return obj.dict() if hasattr(obj, 'dict') else obj.model_dump()
        # Handle Pydantic Url type
        elif hasattr(obj, '__str__') and 'url' in str(type(obj)).lower():
            return str(obj)
        # Handle any object with string representation
        elif hasattr(obj, '__class__') and hasattr(obj, '__str__'):
            if 'pydantic' in str(type(obj)).lower() or 'url' in str(type(obj)).lower():
                return str(obj)
        return super().default(obj)


class JSONExporter:
    """Export scraping results to JSON."""
    
    @staticmethod
    def export(records: List[Any], output_path: str) -> bool:
        """
        Export records to JSON file.
        
        Args:
            records: List of records to export
            output_path: Path to output JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create output directory if it doesn't exist
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data for JSON
            data = []
            for record in records:
                if isinstance(record, BaseModel):
                    data.append(record.dict() if hasattr(record, 'dict') else record.model_dump())
                elif isinstance(record, dict):
                    data.append(record)
                else:
                    data.append(vars(record) if hasattr(record, '__dict__') else record)
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, cls=JSONEncoder, ensure_ascii=False, indent=2)
            
            logger.info(f"Exported {len(records)} records to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export JSON: {str(e)}")
            return False
    
    @staticmethod
    def export_dict(data: Dict[str, Any], output_path: str) -> bool:
        """
        Export dictionary to JSON file.
        
        Args:
            data: Dictionary to export
            output_path: Path to output JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, cls=JSONEncoder, ensure_ascii=False, indent=2)
            
            logger.info(f"Exported data to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export JSON: {str(e)}")
            return False
