"""
Generic HTTP Fetcher with retry logic and rate limiting.

Responsibilities:
- HTTP GET requests
- requests.Session management
- configurable User-Agent, timeout, retry strategy
- rate limiting/delay
- response validation
- useful logging
- clean exception handling
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


@dataclass
class FetchResult:
    """Structured result from a fetch operation."""
    
    url: str
    status_code: Optional[int] = None
    html: str = ""
    success: bool = False
    error: Optional[str] = None
    elapsed_time: float = 0.0
    
    def __post_init__(self):
        """Validate the result structure."""
        if self.status_code and self.status_code == 200:
            self.success = True
        elif self.error:
            self.success = False


class HTTPFetcher:
    """Generic HTTP fetcher with retry logic and rate limiting."""
    
    def __init__(
        self,
        user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        timeout: int = 10,
        delay_seconds: float = 1.0,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        status_forcelist: Optional[list] = None,
    ):
        """
        Initialize the HTTP fetcher.
        
        Args:
            user_agent: Custom User-Agent string
            timeout: Request timeout in seconds
            delay_seconds: Delay between requests for rate limiting
            max_retries: Maximum number of retries
            backoff_factor: Backoff factor for retry strategy
            status_forcelist: HTTP status codes to retry on
        """
        self.user_agent = user_agent
        self.timeout = timeout
        self.delay_seconds = delay_seconds
        self.session = self._init_session(max_retries, backoff_factor, status_forcelist)
        self.last_request_time = 0.0
    
    def _init_session(
        self,
        max_retries: int,
        backoff_factor: float,
        status_forcelist: Optional[list],
    ) -> requests.Session:
        """Initialize requests.Session with retry strategy."""
        if status_forcelist is None:
            status_forcelist = [429, 500, 502, 503, 504]
        
        session = requests.Session()
        session.headers.update({"User-Agent": self.user_agent})
        
        retries = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            raise_on_status=False,
        )
        
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def fetch(self, url: str) -> FetchResult:
        """
        Fetch a URL with rate limiting and retry logic.
        
        Args:
            url: URL to fetch
            
        Returns:
            FetchResult containing status, html, success flag, and error info
        """
        # Rate limiting: respect delay between requests
        elapsed_since_last = time.time() - self.last_request_time
        if elapsed_since_last < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed_since_last)
        
        start_time = time.time()
        
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=self.timeout)
            elapsed_time = time.time() - start_time
            
            # Validate response
            response.raise_for_status()
            
            result = FetchResult(
                url=url,
                status_code=response.status_code,
                html=response.text,
                success=True,
                elapsed_time=elapsed_time,
            )
            
            logger.info(f"Successfully fetched {url} in {elapsed_time:.2f}s")
            self.last_request_time = time.time()
            
            return result
            
        except requests.exceptions.Timeout:
            elapsed_time = time.time() - start_time
            error = f"Timeout after {self.timeout}s"
            logger.error(f"Timeout fetching {url}: {error}")
            return FetchResult(
                url=url,
                status_code=None,
                success=False,
                error=error,
                elapsed_time=elapsed_time,
            )
            
        except requests.exceptions.ConnectionError as e:
            elapsed_time = time.time() - start_time
            error = f"Connection error: {str(e)}"
            logger.error(f"Connection error fetching {url}: {error}")
            return FetchResult(
                url=url,
                status_code=None,
                success=False,
                error=error,
                elapsed_time=elapsed_time,
            )
            
        except requests.exceptions.HTTPError as e:
            elapsed_time = time.time() - start_time
            status_code = e.response.status_code if hasattr(e, 'response') else None
            error = f"HTTP {status_code}: {str(e)}"
            logger.error(f"HTTP error fetching {url}: {error}")
            return FetchResult(
                url=url,
                status_code=status_code,
                success=False,
                error=error,
                elapsed_time=elapsed_time,
            )
            
        except requests.exceptions.RequestException as e:
            elapsed_time = time.time() - start_time
            error = f"Request failed: {str(e)}"
            logger.error(f"Request failed for {url}: {error}")
            return FetchResult(
                url=url,
                status_code=None,
                success=False,
                error=error,
                elapsed_time=elapsed_time,
            )
    
    def close(self):
        """Close the session."""
        self.session.close()
        logger.info("Fetcher session closed")
