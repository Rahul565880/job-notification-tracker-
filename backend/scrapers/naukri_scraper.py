"""Naukri.com job scraper."""
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from backend.scrapers.base_scraper import BaseScraper


class NaukriScraper(BaseScraper):
    """Scraper for Naukri.com job postings."""

    def __init__(self):
        super().__init__("Naukri")

    def fetch_jobs(self, keywords="developer", location="", max_pages=1):
        """Fetch jobs from Naukri.com."""
        jobs = []

        for page in range(max_pages):
            params = {
                "k": keywords,
                "l": location,
                "start": page * 20,
            }
            url = f"https://www.naukri.com/jobs-in-india?{urlencode(params)}"

            response = self.make_request(url)
            if not response:
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            job_cards = (
                soup.find_all("article", class_="jobTuple")
                or soup.find_all("div", class_="jobTuple")
                or soup.find_all("div", class_="tuple")
                or soup.find_all("div", class_="jobCard")
            )

            for card in job_cards:
                try:
                    job = self._parse_job_card(card)
                    if job and job.get("job_url"):
                        jobs.append(self.normalize_job(job))
                except Exception as e:
                    print(f"  Error parsing Naukri card: {e}")
                    continue

        return jobs

    def _parse_job_card(self, card):
        """Parse a single Naukri job card."""
        try:
            title_elem = (
                card.find("a", class_="title")
                or card.find("a", class_="jobTupleHeader")
                or card.find("a", {"data-ga-track": True})
                or card.find("a", href=True)
            )

            if not title_elem:
                return None

            job_url = title_elem.get("href", "")
            if job_url and not job_url.startswith("http"):
                job_url = f"https://www.naukri.com{job_url}"

            job_title = title_elem.get_text(strip=True) if title_elem else ""

            company_elem = (
                card.find("a", class_="subTitle")
                or card.find("div", class_="companyInfo")
                or card.find("span", class_="comp-name")
            )
            company_name = company_elem.get_text(strip=True) if company_elem else "Unknown"

            location_elem = (
                card.find("span", class_="locWdth")
                or card.find("li", class_="location")
                or card.find("span", class_="location")
            )
            location = location_elem.get_text(strip=True) if location_elem else ""

            exp_elem = (
                card.find("span", class_="expwdth")
                or card.find("li", class_="experience")
                or card.find("span", class_="exp")
            )
            experience_level = exp_elem.get_text(strip=True) if exp_elem else ""

            date_elem = card.find("span", class_="date") or card.find("span", class_="posted")
            posted_date = date_elem.get_text(strip=True) if date_elem else ""

            return {
                "job_title": job_title,
                "company_name": company_name,
                "location": location,
                "experience_level": experience_level,
                "job_type": "",
                "posted_date": posted_date,
                "job_url": job_url,
            }
        except Exception as e:
            print(f"  Parse error: {e}")
            return None
