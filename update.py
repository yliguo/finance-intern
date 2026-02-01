import requests
from datetime import datetime, timedelta
import json
import os

URL = "https://www.intern-list.com/api/v1/jobs?selectedKey=💰+Accounting+and+Finance"
CACHE_FILE = "jobs_cache.json"

def fetch_jobs():
    """Fetch all jobs from the JSON feed"""
    jobs = []
    resp = requests.get(URL)
    resp.raise_for_status()
    data = resp.json()

    now = datetime.utcnow()

    for job in data.get("jobs", []):
        company = job.get("company", "").strip()
        role = job.get("title", "").strip()
        posted = job.get("posted_date", "").strip()  # e.g., "2026-01-30"
        location = job.get("location", "").strip()

        try:
            posted_date = datetime.strptime(posted, "%Y-%m-%d")
        except:
            continue

        # Only include jobs posted in last 24h
        if now - posted_date <= timedelta(days=1):
            jobs.append({
                "company": company,
                "role": role,
                "location": location,
                "posted": posted
            })
    return jobs

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_cache(jobs):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2)

def merge_jobs(old_jobs, new_jobs):
    """Merge jobs and remove duplicates based on company + role"""
    merged = { (job["company"], job["role"]): job for job in old_jobs }
    for job in new_jobs:
        merged[(job["company"], job["role"])] = job
    # Keep only jobs posted in last 24h
    now = datetime.utcnow()
    merged_24h = [job for job in merged.values() if now - datetime.strptime(job["posted"], "%Y-%m-%d") <= timedelta(days=1)]
    return merged_24h

# ---- Main ----
new_jobs = fetch_jobs()
old_jobs = load_cache()
all_jobs = merge_jobs(old_jobs, new_jobs)
save_cache(all_jobs)

# ---- Generate HTML ----
now = datetime.utcnow()
html_lines = [
    "<!DOCTYPE html>",
    "<html lang='en'>",
    "<head>",
    "<meta charset='UTF-8'>",
    "<title>Accounting & Finance Internships (Last 24h)</title>",
    "<style>",
    "body { font-family: Arial, sans-serif; padding: 20px; }",
    "table { border-collapse: collapse; width: 100%; }",
    "th, td { border: 1px solid #ccc; padding: 8px; }",
    "th { background: #f2f2f2; }",
    "</style>",
    "</head>",
    "<body>",
    f"<h1>Accounting & Finance Internships (Last 24h)</h1>",
    f"<p>Last updated: {now.strftime('%Y-%m-%d %H:%M UTC')}</p>",
    "<table>",
    "<tr><th>Company</th><th>Role</th><th>Location</th><th>Posted</th></tr>"
]

if all_jobs:
    for job in all_jobs:
        html_lines.append(f"<tr><td>{job['company']}</td><td>{job['role']}</td><td>{job['location']}</td><td>{job['posted']}</td></tr>")
else:
    html_lines.append("<tr><td colspan='4' style='text-align:center;color:#777;'>No internships posted in the past 24 hours</td></tr>")

html_lines.append("</table></body></html>")

with open("index.html", "w", encoding="utf-8") as f:
    f.write("\n".join(html_lines))

print(f"index.html generated successfully with {len(all_jobs)} jobs.")
