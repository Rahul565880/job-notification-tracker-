# Job Notification Tracker

A job tracking application that scrapes job postings from multiple platforms (LinkedIn, Indeed, Naukri), stores them in SQLite, and sends email alerts for new jobs.

## Features

- **Multi-platform scraping** – LinkedIn, Indeed, Naukri
- **Email alerts** – SMTP notifications for new jobs matching keywords/locations
- **Responsive web UI** – Search, filters, dark/light mode
- **Local storage** – Save jobs in the browser
- **Auto-refresh** – Jobs refresh every 5 minutes
- **No authentication** – Direct access to the dashboard

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure (optional)

Create a `.env` file for email alerts:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@gmail.com
ALERT_KEYWORDS=python,developer,software engineer
ALERT_LOCATIONS=remote,hybrid
```

For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833).

### 3. Run the app

```bash
python run.py
```

Or:

```bash
python backend/app.py
```

### 4. Open the UI

Go to [http://localhost:5000](http://localhost:5000).

## Project Structure

```
jonotificationtracker1/
├── backend/
│   ├── app.py           # Flask server
│   ├── database.py      # SQLite operations
│   ├── email_service.py # SMTP notifications
│   ├── scheduler.py     # Scraping scheduler
│   └── scrapers/        # Platform scrapers
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── config.py
├── requirements.txt
└── run.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/jobs | Get all jobs (with optional filters) |
| GET | /api/jobs/new | Get new jobs only |
| POST | /api/jobs/mark-viewed | Mark all jobs as viewed |
| POST | /api/scrape | Trigger scraping manually |
| GET | /api/stats | Get job statistics |

## Configuration

Edit `config.py` to change:

- `SCRAPING_INTERVAL_HOURS` – How often scrapers run (default: 1 hour)
- `RATE_LIMIT_DELAY_SECONDS` – Delay between requests (default: 2 seconds)
- `MAX_RETRIES` – HTTP retries (default: 3)

## Notes

- Scrapers use HTTP requests and may require updates if job sites change their HTML.
- Rate limiting is used to reduce the risk of being blocked.
- Jobs are deduplicated by URL and content hash.
- The app runs without authentication as specified.
