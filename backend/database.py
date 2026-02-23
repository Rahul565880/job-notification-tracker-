"""SQLite database layer for Job Notification Tracker."""
import hashlib
import sqlite3

from config import DATABASE_PATH


def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            company_name TEXT NOT NULL,
            location TEXT,
            experience_level TEXT,
            job_type TEXT,
            posted_date TEXT,
            job_url TEXT NOT NULL,
            source_platform TEXT NOT NULL,
            job_hash TEXT NOT NULL UNIQUE,
            is_new INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform_name TEXT UNIQUE NOT NULL,
            last_scraped TIMESTAMP,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_notifications_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            email_sent_to TEXT NOT NULL,
            email_subject TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_url ON jobs(job_url)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_hash ON jobs(job_hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_source_platform ON jobs(source_platform)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_is_new ON jobs(is_new)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_posted_date ON jobs(posted_date)")

    conn.commit()
    conn.close()


def generate_job_hash(job_url, job_title, company_name):
    """Generate a unique hash for a job."""
    hash_string = f"{job_url}{job_title}{company_name}"
    return hashlib.md5(hash_string.encode()).hexdigest()


def insert_job(job_data):
    """Insert a new job. Returns job_id if new, None if duplicate."""
    conn = get_db_connection()
    cursor = conn.cursor()

    job_hash = generate_job_hash(
        job_data["job_url"],
        job_data["job_title"],
        job_data["company_name"],
    )

    cursor.execute("SELECT id FROM jobs WHERE job_hash = ?", (job_hash,))
    if cursor.fetchone():
        conn.close()
        return None

    cursor.execute("""
        INSERT INTO jobs (
            job_title, company_name, location, experience_level,
            job_type, posted_date, job_url, source_platform, job_hash, is_new
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        job_data["job_title"],
        job_data["company_name"],
        job_data.get("location", ""),
        job_data.get("experience_level", ""),
        job_data.get("job_type", ""),
        job_data.get("posted_date", ""),
        job_data["job_url"],
        job_data["source_platform"],
        job_hash,
    ))

    job_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return job_id


def get_all_jobs(filters=None):
    """Get all jobs with optional filters."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if filters:
        if filters.get("location"):
            query += " AND location LIKE ?"
            params.append(f"%{filters['location']}%")

        if filters.get("experience_level"):
            query += " AND experience_level LIKE ?"
            params.append(f"%{filters['experience_level']}%")

        if filters.get("job_type"):
            query += " AND job_type LIKE ?"
            params.append(f"%{filters['job_type']}%")

        if filters.get("source_platform"):
            query += " AND source_platform = ?"
            params.append(filters["source_platform"])

        if filters.get("search"):
            query += " AND (job_title LIKE ? OR company_name LIKE ?)"
            search_term = f"%{filters['search']}%"
            params.extend([search_term, search_term])

    query += " ORDER BY created_at DESC, posted_date DESC"

    cursor.execute(query, params)
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jobs


def get_new_jobs():
    """Get all jobs marked as new."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE is_new = 1 ORDER BY created_at DESC")
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jobs


def mark_jobs_as_viewed():
    """Mark all new jobs as viewed."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE jobs SET is_new = 0 WHERE is_new = 1")
    conn.commit()
    conn.close()


def log_email_notification(job_id, email_to, email_subject):
    """Log email notification."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO email_notifications_log (job_id, email_sent_to, email_subject) VALUES (?, ?, ?)",
        (job_id, email_to, email_subject),
    )
    conn.commit()
    conn.close()


def update_source_status(platform_name, status="active"):
    """Update or create job source status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO job_sources (platform_name, last_scraped, status) "
        "VALUES (?, CURRENT_TIMESTAMP, ?)",
        (platform_name, status),
    )
    conn.commit()
    conn.close()
