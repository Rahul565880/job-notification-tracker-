"""Configuration for Job Notification Tracker."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Project root
PROJECT_ROOT = Path(__file__).parent

# Database Configuration
DATABASE_PATH = PROJECT_ROOT / "jobs.db"

# Email Configuration (SMTP)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")

# Scraping Configuration
SCRAPING_INTERVAL_HOURS = 1
RATE_LIMIT_DELAY_SECONDS = 2
MAX_RETRIES = 3

# Job Alert Keywords (comma-separated)
ALERT_KEYWORDS = [k.strip() for k in os.getenv("ALERT_KEYWORDS", "python,developer,software engineer").split(",") if k.strip()]

# Job Alert Locations (comma-separated)
ALERT_LOCATIONS = [l.strip() for l in os.getenv("ALERT_LOCATIONS", "remote,hybrid").split(",") if l.strip()]

# Flask Configuration
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True
