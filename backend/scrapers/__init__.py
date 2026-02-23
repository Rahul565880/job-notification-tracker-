"""Job scrapers for multiple platforms."""
from backend.scrapers.linkedin_scraper import LinkedInScraper
from backend.scrapers.indeed_scraper import IndeedScraper
from backend.scrapers.naukri_scraper import NaukriScraper

__all__ = ["LinkedInScraper", "IndeedScraper", "NaukriScraper"]
