from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta

URL = "https://www.intern-list.com/?selectedKey=%F0%9F%92%B0+Accounting+and+Finance&k=af"

def fetch_jobs():
    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL)
        page.wait_for_timeout(3000)  # wait 3 seconds for table to render

        # Get all job roles
        job_titles = page.query_selector_all("p.jobtitle")
        companies = page.query_selector_all("p.companyname_list")
        posted_dates = page.query_selector_all("p.blogtag")

        # Zip them together (assumes they align)
        for c, r, p_date in zip(companies, job_titles, posted_dates):
            company = c.inner_text().strip()
            role = r.inner_text().strip()
            posted = p_date.inner_text().strip()
            # leave location blank for now
            location = ""
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
        # fallback for "Today" / "Yesterday" etc.
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
