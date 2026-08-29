"""
Scraping statistics model.

Tracks metrics during and after scraping for reporting and debugging.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime


@dataclass
class ScrapingStats:
    """Statistics for a scraping job."""
    
    source: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=datetime.now)
    
    pages_requested: int = 0
    pages_fetched: int = 0
    pages_failed: int = 0
    
    records_found: int = 0
    records_valid: int = 0
    records_invalid: int = 0
    
    failed_pages: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> float:
        """Get duration in seconds."""
        return (self.end_time - self.start_time).total_seconds()
    
    @property
    def success_rate(self) -> float:
        """Calculate page success rate as percentage."""
        if self.pages_requested == 0:
            return 0.0
        return (self.pages_fetched / self.pages_requested) * 100
    
    @property
    def record_success_rate(self) -> float:
        """Calculate record validation success rate as percentage."""
        if self.records_found == 0:
            return 0.0
        return (self.records_valid / self.records_found) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "source": self.source,
            "pages_requested": self.pages_requested,
            "pages_fetched": self.pages_fetched,
            "pages_failed": self.pages_failed,
            "records_found": self.records_found,
            "records_valid": self.records_valid,
            "records_invalid": self.records_invalid,
            "duration_seconds": round(self.duration_seconds, 2),
            "page_success_rate": round(self.success_rate, 2),
            "record_success_rate": round(self.record_success_rate, 2),
        }
    
    def print_stats(self):
        """Print statistics in human-readable format."""
        print("\n" + "="*50)
        print("SCRAPING STATISTICS")
        print("="*50)
        print(f"Source: {self.source}")
        print(f"Duration: {self.duration_seconds:.2f}s")
        print(f"\nPages:")
        print(f"  Requested: {self.pages_requested}")
        print(f"  Fetched: {self.pages_fetched}")
        print(f"  Failed: {self.pages_failed}")
        print(f"  Success rate: {self.success_rate:.2f}%")
        print(f"\nRecords:")
        print(f"  Found: {self.records_found}")
        print(f"  Valid: {self.records_valid}")
        print(f"  Invalid: {self.records_invalid}")
        print(f"  Success rate: {self.record_success_rate:.2f}%")
        
        if self.failed_pages:
            print(f"\nFailed pages:")
            for failed in self.failed_pages[:5]:
                print(f"  - {failed.get('url', 'Unknown')}: {failed.get('error', 'Unknown error')}")
        
        print("="*50 + "\n")
