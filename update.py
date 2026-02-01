from playwright.sync_api import sync_playwright
import time
import re

URL = "https://www.intern-list.com/accounting-and-finance-intern-list"

def fetch_all_jobs():
    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 2000})
        page.goto(URL)

        # Wait for the job cards container
        page.wait_for_selector("div[role='listitem']", timeout=30000)

        # Scroll slowly to trigger lazy-loading
        scroll_height = page.evaluate("document.body.scrollHeight")
        for y in range(0, scroll_height, 500):
            page.evaluate(f"window.scrollTo(0, {y})")
            time.sleep(0.5)

        # Grab all job cards
        cards = page.query_selector_all("div[role='listitem']")
        for card in cards:
            role_el = card.query_selector("p.jobtitle")
            company_el = card.query_selector("p.companyname_list")
            if not role_el or not company_el:
                continue

            role = role_el.inner_text().strip()
            company = company_el.inner_text().strip()

            # Try to extract location from role (e.g., " - Chicago - ")
            loc_match = re.search(r" - ([^-]+) - ", role)
            location = loc_match.group(1).strip() if loc_match else ""

            jobs.append((company, role, location))

        browser.close()
    return jobs

# ---- Generate HTML ----
jobs = fetch_all_jobs()

html_lines = [
    "<!DOCTYPE html>",
    "<html lang='en'>",
    "<head>",
    "<meta charset='UTF-8'>",
    "<title>Accounting & Finance Internships</title>",
    "<style>",
    "body { font-family: Arial, sans-serif; padding: 20px; }",
    "table { border-collapse: collapse; width: 100%; }",
    "th, td { border: 1px solid #ccc; padding: 8px; }",
    "th { background: #f2f2f2; }",
    "</style>",
    "</head>",
    "<body>",
    "<h1>Accounting & Finance Internships</h1>",
    "<table>",
    "<tr><th>Company</th><th>Role</th><th>Location</th></tr>"
]

for c, r, l in jobs:
    html_lines.append(f"<tr><td>{c}</td><td>{r}</td><td>{l}</td></tr>")

html_lines.append("</table></body></html>")

with open("index.html", "w", encoding="utf-8") as f:
    f.write("\n".join(html_lines))

print(f"index.html generated successfully with {len(jobs)} jobs.")
