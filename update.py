import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

URL = "https://www.intern-list.com/?selectedKey=%F0%9F%92%B0+Accounting+and+Finance&k=af"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

print("Fetching page...")
resp = requests.get(URL, headers=HEADERS, timeout=30)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")
print(soup.prettify()[:1000])  # print first 1000 chars
rows = soup.select("table tr")

now = datetime.utcnow()
cutoff = now - timedelta(hours=24)

jobs = []

def is_within_24h(posted_text: str) -> bool:
    t = posted_text.lower().strip()

    # Case 1: explicit words
    if "today" in t:
        return True
    if "yesterday" in t:
        return True

    # Case 2: hours (e.g. "5 hours ago", "12h")
    m = re.search(r"(\d+)\s*h", t)
    if m:
        return int(m.group(1)) <= 24

    # Case 3: days (e.g. "1 day ago")
    m = re.search(r"(\d+)\s*d", t)
    if m:
        return int(m.group(1)) <= 1

    return False

print("Parsing rows...")

for r in rows:
    cols = r.find_all("td")
    if len(cols) < 4:
        continue

    company = cols[0].get_text(strip=True)
    role = cols[1].get_text(strip=True)
    location = cols[2].get_text(strip=True)
    posted = cols[3].get_text(strip=True)

    if not company or not role:
        continue

    if is_within_24h(posted):
        jobs.append((company, role, location, posted))

print(f"Jobs found in last 24h: {len(jobs)}")

# ---- Generate HTML ----
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

print("index.html generated successfully.")
