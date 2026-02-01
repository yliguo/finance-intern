import requests
import datetime
import re
from pathlib import Path

# CONFIG
TARGET_REPO = "https://raw.githubusercontent.com/jobright-ai/2026-Account-Internship/master/README.md"
OUTPUT_FILE = Path("data/latest_24h.md")

def fetch_readme():
    r = requests.get(TARGET_REPO)
    r.raise_for_status()
    return r.text

def parse_jobs(md_text):
    """
    Extract table rows from README.md
    Only keep rows with dates within last 24 hours
    """
    lines = md_text.splitlines()
    table = []
    date_pattern = re.compile(r"\b(\w+ \d{1,2})(?:,? \d{4})?$")

    now = datetime.datetime.utcnow()
    for line in lines:
        # Skip header and empty lines
        if "|" not in line:
            continue

        parts = line.split("|")
        if len(parts) < 5:
            continue

        # Try to read date (last column)
        date_str = parts[-1].strip()
        match = date_pattern.search(date_str)
        if not match:
            continue

        try:
            dt = datetime.datetime.strptime(match.group(1) + f" {now.year}", "%b %d %Y")
        except ValueError:
            continue

        # Only add if within 24 hours
        if now - dt <= datetime.timedelta(days=1):
            table.append(line)

    return table

def save_output(jobs):
    output = "# Latest Internships (Last 24h)\n\n"
    output += "| Company | Job Title | Location | Work Model | Date Posted |\n"
    output += "|---|---|---|---|---|\n"
    output += "\n".join(jobs)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(output)

def main():
    md = fetch_readme()
    jobs = parse_jobs(md)
    save_output(jobs)
    print(f"Saved {len(jobs)} internships.")

if __name__ == "__main__":
    main()
