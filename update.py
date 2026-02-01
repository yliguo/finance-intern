from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import time

URL = "https://www.intern-list.com/?selectedKey=%F0%9F%92%B0+Accounting+and+Finance&k=af"

def fetch_jobs():
    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL)
        # Wait for the table to load (adjust if needed)
        page.wait_for_timeout(3000)  # wait 3 seconds
        # Get all table rows
        rows = page.query_selector_all("table tr")
        for r in rows[1:]:  # skip header
            cells = r.query_selector_all("td")
            if len(cells) < 4:
                continue
            company = cells[0].inner_text().strip()
            role = cells[1].inner_text().strip()
            location = cells[2].inner_text().strip()
            posted = cells[3].inner_text().strip()
            # filter last 24h
            if is_within_24h(posted):
                jobs.append((company, role, location, posted))
        browser.close()
    return jobs

def is_within_24h(posted_text: str) -> bool:
    t = posted_text.lower().strip()
    now = datetime.utcnow()
    # Case 1: today
    if "today" in t:
        return True
    # Case 2: yesterday
    if "yesterday" in t:
        return True
    # Case 3: hours like "5h" or "5 hours ago"
    import re
    m = re.search(r"(\d+)\s*h", t)
    if m and int(m.group(1)) <= 24:
        return True
    # Case 4: days like "1 day ago"
    m = re.search(r"(\d+)\s*d", t)
    if m and int(m.group(1)) <= 1:
        return True
    return False

# ---- Generate HTML ----
jobs = fetch_jobs()
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

if jobs:
    for c, r, l, p in jobs:
        html_lines.append(f"<tr><td>{c}</td><td>{r}</td><td>{l}</td><td>{p}</td></tr>")
else:
    html_lines.append("<tr><td colspan='4' style='text-align:center;color:#777;'>No internships posted in the past 24 hours</td></tr>")

html_lines.append("</table></body></html>")

with open("index.html", "w", encoding="utf-8") as f:
    f.write("\n".join(html_lines))

print(f"index.html generated successfully with {len(jobs)} jobs.")
