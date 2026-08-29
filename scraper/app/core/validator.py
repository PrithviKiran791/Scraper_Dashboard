"""
Validator for validating extracted records using Pydantic models.

Responsibilities:
- Validate extracted records using Pydantic models
- Report validation errors
- Do not crash the entire scraping job because one record is invalid
- Provide useful validation statistics
"""

import logging
from typing import Type, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of validating a single record."""
    
    valid: bool
    record: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class ValidationStats:
    """Statistics for validation run."""
    
    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    errors: List[str] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_records == 0:
            return 0.0
        return (self.valid_records / self.total_records) * 100


class Validator:
    """Generic validator using Pydantic models."""
    
    def __init__(self, model: Type[BaseModel]):
        """
        Initialize the validator with a Pydantic model.
        
        Args:
            model: Pydantic model class to validate against
        """
        self.model = model
        self.stats = ValidationStats()
    
    def validate(self, record: Dict[str, Any]) -> ValidationResult:
        """
        Validate a single record.
        
        Args:
            record: Dictionary to validate
            
        Returns:
            ValidationResult with valid flag and errors
        """
        try:
            # Try to create model instance
            instance = self.model(**record)
            
            self.stats.valid_records += 1
            self.stats.total_records += 1
            
            logger.debug(f"Record validated successfully")
            
            return ValidationResult(
                valid=True,
                record=instance.dict() if hasattr(instance, 'dict') else record
            )
            
        except ValidationError as e:
            self.stats.invalid_records += 1
            self.stats.total_records += 1
            
            # Extract error messages
            errors = []
            for error in e.errors():
                field_path = ".".join(str(x) for x in error['loc'])
                msg = error['msg']
                errors.append(f"{field_path}: {msg}")
            
            self.stats.errors.extend(errors)
            
            logger.warning(f"Validation failed: {'; '.join(errors)}")
            
            return ValidationResult(
                valid=False,
                record=record,
                errors=errors
            )
        
        except Exception as e:
            self.stats.invalid_records += 1
            self.stats.total_records += 1
            
            error_msg = f"Unexpected error: {str(e)}"
            self.stats.errors.append(error_msg)
            
            logger.error(error_msg)
            
            return ValidationResult(
                valid=False,
                record=record,
                errors=[error_msg]
            )
    
    def validate_batch(self, records: List[Dict[str, Any]]) -> Tuple[List[BaseModel], List[ValidationResult]]:
        """
        Validate multiple records.
        
        Args:
            records: List of dictionaries to validate
            
        Returns:
            Tuple of (valid_instances, all_results)
        """
        valid_instances = []
        all_results = []
        
        for record in records:
            result = self.validate(record)
            all_results.append(result)
            
            if result.valid:
                try:
                    instance = self.model(**record)
                    valid_instances.append(instance)
                except Exception as e:
                    logger.error(f"Error creating model instance: {str(e)}")
        
        return valid_instances, all_results
    
    def get_stats(self) -> ValidationStats:
        """Get validation statistics."""
        return self.stats
    
    def reset_stats(self):
        """Reset validation statistics."""
        self.stats = ValidationStats()
    
    def print_stats(self):
        """Print validation statistics in human-readable format."""
        print("\n" + "="*50)
        print("VALIDATION STATISTICS")
        print("="*50)
        print(f"Total records: {self.stats.total_records}")
        print(f"Valid records: {self.stats.valid_records}")
        print(f"Invalid records: {self.stats.invalid_records}")
        print(f"Success rate: {self.stats.success_rate:.2f}%")
        
        if self.stats.errors:
            print(f"\nTop errors:")
            # Show unique errors
            unique_errors = list(set(self.stats.errors))[:5]
            for i, error in enumerate(unique_errors, 1):
                print(f"  {i}. {error}")
        
        print("="*50 + "\n")
