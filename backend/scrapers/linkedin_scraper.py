"""LinkedIn job scraper."""
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from backend.scrapers.base_scraper import BaseScraper


class LinkedInScraper(BaseScraper):
    """Scraper for LinkedIn job postings."""

    def __init__(self):
        super().__init__("LinkedIn")

    def fetch_jobs(self, keywords="developer", location="", max_pages=1):
        """Fetch jobs from LinkedIn public job search."""
        jobs = []

        for page in range(max_pages):
            params = {
                "keywords": keywords,
                "location": location,
                "start": page * 25,
            }
            url = f"https://www.linkedin.com/jobs/search/?{urlencode(params)}"

            response = self.make_request(url)
            if not response:
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            job_cards = (
                soup.find_all("div", class_="base-card")
                or soup.find_all("li", class_="result-card")
                or soup.find_all("div", class_="job-search-card")
            )

            for card in job_cards:
                try:
                    job = self._parse_job_card(card)
                    if job and job.get("job_url"):
                        jobs.append(self.normalize_job(job))
                except Exception as e:
                    print(f"  Error parsing LinkedIn card: {e}")
                    continue

        return jobs

    def _parse_job_card(self, card):
        """Parse a single LinkedIn job card."""
        try:
            title_elem = (
                card.find("h3", class_="base-search-card__title")
                or card.find("h3", class_="result-card__title")
                or card.find("h3", class_="job-search-card__title")
                or card.find("h3")
            )
            if not title_elem:
                return None

            link_elem = title_elem.find("a") or card.find("a", href=True)
            job_url = link_elem.get("href", "") if link_elem else ""

            if job_url and not job_url.startswith("http"):
                job_url = f"https://www.linkedin.com{job_url}"

            job_title = (link_elem or title_elem).get_text(strip=True) if link_elem or title_elem else ""

            company_elem = (
                card.find("h4", class_="base-search-card__subtitle")
                or card.find("h4", class_="result-card__subtitle")
                or card.find("a", class_="hidden-nested-link")
            )
            company_name = company_elem.get_text(strip=True) if company_elem else "Unknown"

            location_elem = (
                card.find("span", class_="job-search-card__location")
                or card.find("span", class_="result-card__location")
                or card.find("span", class_="job-search-card__location")
            )
            location = location_elem.get_text(strip=True) if location_elem else ""

            date_elem = (
                card.find("time", class_="job-search-card__listdate")
                or card.find("time", class_="result-card__listdate")
                or card.find("time")
            )
            posted_date = date_elem.get("datetime", "") if date_elem and date_elem.get("datetime") else ""

            return {
                "job_title": job_title,
                "company_name": company_name,
                "location": location,
                "experience_level": "",
                "job_type": "",
                "posted_date": posted_date,
                "job_url": job_url,
            }
        except Exception as e:
            print(f"  Parse error: {e}")
            return None
