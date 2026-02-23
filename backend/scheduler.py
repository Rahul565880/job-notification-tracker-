"""Scheduler for running scrapers at fixed intervals."""
import schedule
import threading
import time

from config import SCRAPING_INTERVAL_HOURS
from backend.database import insert_job, update_source_status
from backend.email_service import EmailService
from backend.scrapers import IndeedScraper, LinkedInScraper, NaukriScraper


class JobScheduler:
    """Scheduler for running scrapers at intervals."""

    def __init__(self):
        self.scrapers = [
            LinkedInScraper(),
            IndeedScraper(),
            NaukriScraper(),
        ]
        self.email_service = EmailService()
        self.running = False

    def scrape_all_platforms(self):
        """Scrape jobs from all platforms and send alerts for new ones."""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting scheduled scraping...")
        new_jobs = []

        for scraper in self.scrapers:
            try:
                print(f"  Scraping {scraper.platform_name}...")
                jobs = scraper.fetch_jobs(keywords="developer", location="", max_pages=1)

                for job in jobs:
                    job_id = insert_job(job)
                    if job_id:
                        new_jobs.append({**job, "id": job_id})
                        print(f"    New: {job['job_title']} at {job['company_name']}")

                update_source_status(scraper.platform_name, "active")
                print(f"  {scraper.platform_name}: {len(jobs)} jobs found")
            except Exception as e:
                print(f"  Error scraping {scraper.platform_name}: {e}")
                update_source_status(scraper.platform_name, "error")

        if new_jobs:
            self.email_service.send_batch_alert(new_jobs)

        print(f"  Done. {len(new_jobs)} new jobs added.\n")
        return new_jobs

    def start(self):
        """Start the scheduler."""
        if self.running:
            return

        self.running = True
        schedule.every(SCRAPING_INTERVAL_HOURS).hours.do(self.scrape_all_platforms)

        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(60)

        t = threading.Thread(target=run_scheduler, daemon=True)
        t.start()
        print(f"Scheduler started. Scraping every {SCRAPING_INTERVAL_HOURS} hour(s).\n")

    def stop(self):
        """Stop the scheduler."""
        self.running = False
        schedule.clear()
        print("Scheduler stopped.")
