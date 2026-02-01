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
