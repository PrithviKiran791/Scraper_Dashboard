"""
CSV Exporter for saving scraping results.

Responsibilities:
- Dynamically determine fields
- Flatten simple Pydantic models
- Correctly serialize optional fields
- UTF-8 encoding
"""

import csv
import logging
from typing import List, Any, Dict, Set
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class CSVExporter:
    """Export scraping results to CSV."""
    
    @staticmethod
    def _flatten_record(record: Any) -> Dict[str, Any]:
        """
        Flatten a record to a dictionary.
        
        Args:
            record: Record to flatten
            
        Returns:
            Flattened dictionary
        """
        if isinstance(record, BaseModel):
            return record.dict() if hasattr(record, 'dict') else record.model_dump()
        elif isinstance(record, dict):
            return record
        else:
            return vars(record) if hasattr(record, '__dict__') else {}
    
    @staticmethod
    def _get_field_names(records: List[Any]) -> List[str]:
        """
        Extract unique field names from records.
        
        Args:
            records: List of records
            
        Returns:
            List of field names
        """
        field_names: Set[str] = set()
        
        for record in records:
            flat = CSVExporter._flatten_record(record)
            field_names.update(flat.keys())
        
        return sorted(list(field_names))
    
    @staticmethod
    def _serialize_value(value: Any) -> str:
        """
        Serialize a value to string for CSV.
        
        Args:
            value: Value to serialize
            
        Returns:
            String representation
        """
        if value is None:
            return ""
        elif isinstance(value, bool):
            return "True" if value else "False"
        elif isinstance(value, (Decimal, float)):
            return str(float(value))
        elif isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, (list, dict)):
            # For complex types, convert to string
            return str(value)
        else:
            return str(value)
    
    @staticmethod
    def export(records: List[Any], output_path: str) -> bool:
        """
        Export records to CSV file.
        
        Args:
            records: List of records to export
            output_path: Path to output CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not records:
                logger.warning("No records to export")
                return False
            
            # Create output directory if it doesn't exist
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Get field names from records
            field_names = CSVExporter._get_field_names(records)
            
            # Write to file
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=field_names)
                
                # Write header
                writer.writeheader()
                
                # Write records
                for record in records:
                    flat = CSVExporter._flatten_record(record)
                    
                    # Serialize all values
                    serialized = {
                        key: CSVExporter._serialize_value(flat.get(key))
                        for key in field_names
                    }
                    
                    writer.writerow(serialized)
            
            logger.info(f"Exported {len(records)} records to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export CSV: {str(e)}")
            return False
