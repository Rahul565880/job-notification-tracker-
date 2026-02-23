"""Base scraper interface for job platforms."""
import time
from abc import ABC, abstractmethod

import requests

from config import MAX_RETRIES, RATE_LIMIT_DELAY_SECONDS


class BaseScraper(ABC):
    """Base class for all job scrapers."""

    def __init__(self, platform_name):
        self.platform_name = platform_name
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })

    @abstractmethod
    def fetch_jobs(self, keywords=None, location=None, max_pages=1):
        """
        Fetch jobs from the platform.

        Args:
            keywords: Search keywords
            location: Location filter
            max_pages: Maximum pages to scrape

        Returns:
            List of job dictionaries in normalized format
        """
        pass

    def normalize_job(self, raw_job):
        """Normalize job data to standard format."""
        return {
            "job_title": raw_job.get("job_title", ""),
            "company_name": raw_job.get("company_name", ""),
            "location": raw_job.get("location", ""),
            "experience_level": raw_job.get("experience_level", ""),
            "job_type": raw_job.get("job_type", ""),
            "posted_date": raw_job.get("posted_date", ""),
            "job_url": raw_job.get("job_url", ""),
            "source_platform": self.platform_name,
        }

    def make_request(self, url, retries=MAX_RETRIES):
        """Make HTTP request with retries and rate limiting."""
        for attempt in range(retries):
            try:
                time.sleep(RATE_LIMIT_DELAY_SECONDS)
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                if attempt == retries - 1:
                    print(f"  Error fetching {url} after {retries} attempts: {e}")
                    return None
                time.sleep(2**attempt)
        return None
