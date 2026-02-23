"""SMTP-based email notification service."""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import (
    ALERT_KEYWORDS,
    ALERT_LOCATIONS,
    EMAIL_FROM,
    EMAIL_TO,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_SERVER,
    SMTP_USERNAME,
)
from backend.database import log_email_notification


class EmailService:
    """Service for sending job alert email notifications."""

    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.username = SMTP_USERNAME
        self.password = SMTP_PASSWORD
        self.email_from = EMAIL_FROM
        self.email_to = EMAIL_TO

    def should_send_alert(self, job):
        """Check if job matches alert criteria (keywords and/or locations)."""
        if not ALERT_KEYWORDS and not ALERT_LOCATIONS:
            return True

        job_title_lower = (job.get("job_title") or "").lower()
        location_lower = (job.get("location") or "").lower()

        if ALERT_KEYWORDS:
            if not any(kw.lower() in job_title_lower for kw in ALERT_KEYWORDS if kw):
                return False

        if ALERT_LOCATIONS:
            if not any(loc.lower() in location_lower for loc in ALERT_LOCATIONS if loc):
                return False

        return True

    def send_job_alert(self, job):
        """Send email alert for a single job."""
        if not self.should_send_alert(job):
            return False

        if not self.email_from or not self.email_to or not self.username or not self.password:
            print("  Email configuration missing. Skipping email alert.")
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_from
            msg["To"] = self.email_to
            msg["Subject"] = f"New Job: {job['job_title']} at {job['company_name']}"

            body = f"""
New Job Opportunity Found!

Job Title: {job['job_title']}
Company: {job['company_name']}
Location: {job.get('location', 'Not specified')}
Experience Level: {job.get('experience_level', 'Not specified')}
Job Type: {job.get('job_type', 'Not specified')}
Posted Date: {job.get('posted_date', 'Not specified')}
Source: {job['source_platform']}

Apply here: {job['job_url']}

---
Automated notification from Job Notification Tracker.
"""
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            log_email_notification(job.get("id"), self.email_to, msg["Subject"])
            print(f"  Email alert sent for: {job['job_title']}")
            return True

        except Exception as e:
            print(f"  Error sending email: {e}")
            return False

    def send_batch_alert(self, jobs):
        """Send batched email alert for multiple jobs."""
        if not jobs:
            return False

        if not self.email_from or not self.email_to or not self.username or not self.password:
            print("  Email configuration missing. Skipping batch alert.")
            return False

        filtered = [j for j in jobs if self.should_send_alert(j)]
        if not filtered:
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_from
            msg["To"] = self.email_to
            msg["Subject"] = f"Job Alert: {len(filtered)} New Job(s) Found"

            body = f"Found {len(filtered)} new job(s):\n\n"
            for idx, job in enumerate(filtered, 1):
                body += f"{idx}. {job['job_title']} at {job['company_name']}\n"
                body += f"   Location: {job.get('location', 'N/A')}\n"
                body += f"   Source: {job['source_platform']}\n"
                body += f"   Apply: {job['job_url']}\n\n"

            body += "\n---\nAutomated notification from Job Notification Tracker."
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            for job in filtered:
                log_email_notification(job.get("id"), self.email_to, msg["Subject"])

            print(f"  Batch email sent for {len(filtered)} job(s)")
            return True

        except Exception as e:
            print(f"  Error sending batch email: {e}")
            return False
