from playwright.sync_api import sync_playwright

URL = "https://www.intern-list.com/?selectedKey=%F0%9F%92%B0+Accounting+and+Finance&utm_source=1101&utm_campaign=Accounting+and+Finance&k=af"

def fetch_all_jobs():
    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL)

        # Wait for the internship list to appear
        page.wait_for_selector("div[role='listitem']", timeout=30000)

        # Get all internship cards
        cards = page.query_selector_all("div[role='listitem']")
        for card in cards:
            role_el = card.query_selector("p.jobtitle")
            company_el = card.query_selector("p.companyname_list")
            location = ""  # Some listings have location in the role text
            if role_el and company_el:
                role = role_el.inner_text().strip()
                company = company_el.inner_text().strip()
                # Try to extract location from role (e.g., " - Chicago - ")
                import re
                loc_match = re.search(r" - ([^-]+) - ", role)
                if loc_match:
                    location = loc_match.group(1).strip()
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
