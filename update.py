import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

URL = "https://www.intern-list.com/?selectedKey=%F0%9F%92%B0+Accounting+and+Finance&k=af"

html = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}).text
soup = BeautifulSoup(html, "html.parser")

rows = soup.select("table tr")
now = datetime.utcnow()
cutoff = now - timedelta(hours=24)

jobs = []

for r in rows:
    cols = r.find_all("td")
    if len(cols) < 4:
        continue

    posted = cols[3].get_text(strip=True).lower()

    # example: "6 hours ago"
    if "hour" in posted:
        hours = int(posted.split()[0])
        if hours <= 24:
            jobs.append([
                cols[0].get_text(strip=True),
                cols[1].get_text(strip=True),
                cols[2].get_text(strip=True),
                posted
            ])

with open("index.html", "w", encoding="utf-8") as f:
    f.write("""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>Internships – Last 24 Hours</title>
<style>
table{border-collapse:collapse;width:100%}
td,th{border:1px solid #ccc;padding:8px}
th{background:#eee}
</style>
</head><body>
<h1>Accounting & Finance Internships (Last 24h)</h1>
<table>
<tr><th>Company</th><th>Role</th><th>Location</th><th>Posted</th></tr>
""")
    for j in jobs:
        f.write("<tr>" + "".join(f"<td>{c}</td>" for c in j) + "</tr>")
    f.write("</table></body></html>")
