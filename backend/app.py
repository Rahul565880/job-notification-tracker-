"""Flask backend for Job Notification Tracker."""
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from config import FLASK_DEBUG, FLASK_HOST, FLASK_PORT, PROJECT_ROOT
from backend.database import (
    get_all_jobs,
    get_new_jobs,
    init_database,
    mark_jobs_as_viewed,
)
from backend.scheduler import JobScheduler

app = Flask(__name__, static_folder=str(PROJECT_ROOT / "frontend"))
CORS(app)

frontend_dir = PROJECT_ROOT / "frontend"
scheduler = JobScheduler()


@app.route("/")
def index():
    """Serve the main HTML page."""
    return send_from_directory(frontend_dir, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    """Serve static files from frontend."""
    return send_from_directory(frontend_dir, path)


@app.route("/api/jobs", methods=["GET"])
def api_get_jobs():
    """Get all jobs with optional filters."""
    filters = {
        "search": request.args.get("search", "").strip(),
        "location": request.args.get("location", "").strip(),
        "experience_level": request.args.get("experience", "").strip(),
        "job_type": request.args.get("job_type", "").strip(),
        "source_platform": request.args.get("source", "").strip(),
    }
    filters = {k: v for k, v in filters.items() if v}

    jobs = get_all_jobs(filters)
    return jsonify({"jobs": jobs, "count": len(jobs)})


@app.route("/api/jobs/new", methods=["GET"])
def api_get_new_jobs():
    """Get all new jobs."""
    jobs = get_new_jobs()
    return jsonify({"jobs": jobs, "count": len(jobs)})


@app.route("/api/jobs/mark-viewed", methods=["POST"])
def api_mark_viewed():
    """Mark all jobs as viewed."""
    mark_jobs_as_viewed()
    return jsonify({"message": "All jobs marked as viewed"})


@app.route("/api/scrape", methods=["POST"])
def api_trigger_scrape():
    """Manually trigger scraping."""
    try:
        new_jobs = scheduler.scrape_all_platforms()
        return jsonify({
            "message": "Scraping completed",
            "new_jobs_count": len(new_jobs),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats", methods=["GET"])
def api_get_stats():
    """Get statistics about jobs."""
    all_jobs = get_all_jobs()
    new_jobs = get_new_jobs()

    platform_counts = {}
    for job in all_jobs:
        p = job.get("source_platform", "Unknown")
        platform_counts[p] = platform_counts.get(p, 0) + 1

    return jsonify({
        "total_jobs": len(all_jobs),
        "new_jobs": len(new_jobs),
        "platform_counts": platform_counts,
    })


def main():
    init_database()
    scheduler.start()
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)


if __name__ == "__main__":
    main()
