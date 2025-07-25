import json
from datetime import datetime, timedelta, timezone
import pandas as pd

INPUT_PATH = 'output/live_verified_fires.json'
OUTPUT_JSON_PATH = 'output/final_verified_fires.json'
OUTPUT_XLSX_PATH = 'output/final_verified_fires.xlsx'

# Load the data
with open(INPUT_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get current UTC time (timezone-aware)
now = datetime.now(timezone.utc)
print(f"Current UTC time: {now.isoformat()}\n")

# Filter entries from the last 72 hours
filtered = []
for i, entry in enumerate(data):
    ts = entry.get('published_date', '')
    try:
        tweet_time = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        diff_hours = (now - tweet_time).total_seconds() / 3600
        include = (now - tweet_time).total_seconds() <= 72 * 3600
        print(f"[{i}] published_date: {ts} | parsed: {tweet_time.isoformat()} | diff_hours: {diff_hours:.2f} | included: {include}")
        if include:
            filtered.append(entry)
    except Exception as e:
        print(f"[{i}] published_date: {ts} | ERROR: {e}")
        continue

# Save the filtered entries as JSON
with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(filtered, f, indent=2, ensure_ascii=False)

print(f"\nExtracted {len(filtered)} entries from the last 3 days to {OUTPUT_JSON_PATH}")

# Save the filtered entries as Excel
if filtered:
    df = pd.DataFrame(filtered)
    df.to_excel(OUTPUT_XLSX_PATH, index=False)
    print(f"Also saved {len(filtered)} entries to {OUTPUT_XLSX_PATH}")
else:
    print("No entries to save to Excel.") 