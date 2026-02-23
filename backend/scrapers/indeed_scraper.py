"""Indeed job scraper."""
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from backend.scrapers.base_scraper import BaseScraper


class IndeedScraper(BaseScraper):
    """Scraper for Indeed job postings."""

    def __init__(self):
        super().__init__("Indeed")

    def fetch_jobs(self, keywords="developer", location="", max_pages=1):
        """Fetch jobs from Indeed."""
        jobs = []

        for page in range(max_pages):
            params = {
                "q": keywords,
                "l": location,
                "start": page * 10,
            }
            url = f"https://www.indeed.com/jobs?{urlencode(params)}"

            response = self.make_request(url)
            if not response:
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            job_cards = (
                soup.find_all("div", class_="job_seen_beacon")
                or soup.find_all("div", class_="jobsearch-ResultsList")
                or soup.find_all("div", {"data-jk": True})
            )

            for card in job_cards:
                if card.name == "div" and "jobsearch-ResultsList" in (card.get("class") or []):
                    sub_cards = card.find_all("div", class_="job_seen_beacon") or card.find_all("div", {"data-jk": True})
                    for sub in sub_cards:
                        try:
                            job = self._parse_job_card(sub)
                            if job and job.get("job_url"):
                                jobs.append(self.normalize_job(job))
                        except Exception as e:
                            print(f"  Error parsing Indeed card: {e}")
                    continue

                try:
                    job = self._parse_job_card(card)
                    if job and job.get("job_url"):
                        jobs.append(self.normalize_job(job))
                except Exception as e:
                    print(f"  Error parsing Indeed card: {e}")
                    continue

        return jobs

    def _parse_job_card(self, card):
        """Parse a single Indeed job card."""
        try:
            title_elem = (
                card.find("h2", class_="jobTitle")
                or card.find("span", id=lambda x: x and "jobTitle" in str(x))
                or card.find("a", {"data-jk": True})
            )

            if not title_elem:
                return None

            link_elem = title_elem if title_elem.name == "a" else title_elem.find("a", href=True)
            if not link_elem:
                return None

            job_url = link_elem.get("href", "")
            if job_url and not job_url.startswith("http"):
                job_url = f"https://www.indeed.com{job_url}"

            job_title = link_elem.get_text(strip=True) if link_elem else ""

            company_elem = (
                card.find("span", class_="companyName")
                or card.find("span", {"data-testid": "company-name"})
            )
            company_name = company_elem.get_text(strip=True) if company_elem else "Unknown"

            location_elem = (
                card.find("div", class_="companyLocation")
                or card.find("div", {"data-testid": "text-location"})
            )
            location = location_elem.get_text(strip=True) if location_elem else ""

            date_elem = card.find("span", class_="date") or card.find("span", {"data-testid": "myJobsStateDate"})
            posted_date = date_elem.get_text(strip=True) if date_elem else ""

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
