import requests

SOURCE_README = (
    "https://raw.githubusercontent.com/"
    "jobright-ai/2026-Account-Internship/master/README.md"
)

def fetch_source():
    r = requests.get(SOURCE_README, timeout=30)
    r.raise_for_status()
    return r.text

def extract_table(md):
    lines = md.splitlines()
    table = []
    in_table = False

    for line in lines:
        if line.startswith("| Company"):
            in_table = True
            table.append(line)
            continue
        if in_table and line.startswith("|---"):
            table.append(line)
            continue
        if in_table:
            if not line.startswith("|"):
                break
            table.append(line)

    return table

def build_readme(table):
    header = """# 💼 Finance & Accounting Internships (Live)

Automatically synced from **jobright-ai/2026-Account-Internship**  
⏱ Updated every 3 hours via GitHub Actions

---
"""
    if not table:
        return header + "\n_No internship data found._\n"

    return header + "\n".join(table) + "\n"

def main():
    source = fetch_source()
    table = extract_table(source)
    readme = build_readme(table)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

if __name__ == "__main__":
    main()
