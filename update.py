from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import re

URL = "https://www.intern-list.com/?selectedKey=%F0%9F%92%B0+Accounting+and+Finance&k=af"

def fetch_jobs():
    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL)

        # Wait for the internship cards to appear (up to 15s)
        page.wait_for_selector("div[role='listitem']", timeout=15000)

        # Select all internship cards
        cards = page.query_selector_all("div[role='listitem']")
        for card in cards:
            role_el = card.query_selector("p.jobtitle")
            company_el = card.query_selector("p.companyname_list")
            posted_el = card.query_selector("p.blogtag")

            if not role_el or not company_el or not posted_el:
                continue

            role = role_el.inner_text().strip()
            company = company_el.inner_text().strip()
            posted = posted_el.inner_text().strip()

            # Extract location from role if present (e.g., " - Chicago - " in title)
            location_match = re.search(r" - ([^-]+) - ", role)
            location = location_match.group(1).strip() if location_match else ""

            if is_within_24h(posted):
                jobs.append((company, role, location, posted))

        browser.close()
    return jobs

def is_within_24h(posted_text: str) -> bool:
    posted_text = posted_text.strip()
    now = datetime.utcnow()

    # Try parsing date like "January 30, 2026"
    try:
        posted_date = datetime.strptime(posted_text, "%B %d, %Y")
        return now - posted_date <= timedelta(days=1)
    except:
        # fallback for "Today" / "Yesterday"
        t = posted_text.lower()
        if "today" in t or "yesterday" in t:
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
