import requests
import json
from pathlib import Path
from datetime import datetime

# Config
SOURCE_README = (
    "https://raw.githubusercontent.com/jobright-ai/2026-Account-Internship/master/README.md"
)
HISTORY_FILE = Path("data/history.json")
MAX_HISTORY = 8  # keep last 8 runs

def fetch_source():
    r = requests.get(SOURCE_README, timeout=30)
    r.raise_for_status()
    return r.text

def extract_table(md):
    """Extract table rows from Jobright README"""
    lines = md.splitlines()
    table = []
    in_table = False
    for line in lines:
        if line.startswith("| Company"):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table:
            if not line.startswith("|"):
                break
            table.append(line.strip())
    return table

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def build_readme(history):
    header = """# 💼 Finance & Accounting Internships (Live)

Automatically synced from **jobright-ai/2026-Account-Internship**  
⏱ Updated every 3 hours via GitHub Actions

---
"""
    if not history:
        return header + "_No internships found in last 24 hours_\n"

    # Flatten all rows from history into a single Markdown table
    table_md = "| Company | Role | Location | Type | Date Posted | Link |\n"
    table_md += "|--------|------|----------|------|-------------|------|\n"
    for batch in history:
        for row in batch:
            table_md += row + "\n"
    return header + table_md

def main():
    source = fetch_source()
    new_rows = extract_table(source)

    if not new_rows:
        print("No new rows found. Exiting.")
        return

    # Load previous history
    history = load_history()

    # Add new batch at the start
    history.insert(0, new_rows)

    # Keep only the last MAX_HISTORY batches
    history = history[:MAX_HISTORY]

    # Save updated history
    save_history(history)

    # Build README.md
    readme = build_readme(history)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"Saved README with {len(new_rows)} new rows. Total batches: {len(history)}")

if __name__ == "__main__":
    main()
