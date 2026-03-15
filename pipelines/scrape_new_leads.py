#!/usr/bin/env python3
"""
Scrape new leads from Google Maps and append to salon_leads.csv.
Usage: scrape_new_leads.py "hair salons Minneapolis" 30 "Minneapolis"
"""

import subprocess, json, csv, sys
from pathlib import Path

workspace = Path('/root/.openclaw/workspace')
salon_leads_csv = workspace / 'salon_leads.csv'
node_script = workspace / 'skills/playwright-scraper/scripts/google-maps-scrape-v2.js'

if len(sys.argv) < 3:
    print("Usage: scrape_new_leads.py <query> <max_results> [city]")
    sys.exit(1)

query = sys.argv[1]
max_results = int(sys.argv[2])
city = sys.argv[3] if len(sys.argv) > 3 else ''

# Run node scraper
cmd = ['node', str(node_script), query, str(max_results)]
try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        print(f"Scraper error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(result.stdout)
except Exception as e:
    print(f"Failed to run scraper: {e}", file=sys.stderr)
    sys.exit(1)

# Desired unified fieldnames (include city)
FIELDNAMES = ['business_name','website','phone','has_website','booking_platform','owner_first_name','email','notes','city']

# Load existing CSV if present
existing_rows = []
existing_header = []
if salon_leads_csv.exists():
    with open(salon_leads_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        existing_header = reader.fieldnames or []
        for row in reader:
            existing_rows.append(row)

# Determine final header: FIELDNAMES order, plus any extra fields from existing
final_header = FIELDNAMES[:]
for field in existing_header:
    if field not in final_header:
        final_header.append(field)

# Build set of existing business names (lowercase) for deduplication
existing_names = set()
for row in existing_rows:
    name = row.get('business_name', '').strip().lower()
    if name:
        existing_names.add(name)

# Prepare new rows (only those not already present)
new_rows = []
for item in data:
    name = item.get('name', '').strip()
    if not name:
        continue
    if name.lower() in existing_names:
        continue
    row = {field: '' for field in final_header}
    row['business_name'] = name
    row['website'] = item.get('website', '')
    row['phone'] = item.get('phone', '')
    row['has_website'] = str(item.get('has_website', '')).lower()
    row['city'] = city
    new_rows.append(row)

if not new_rows:
    print("No new leads to add.")
    sys.exit(0)

# Combine existing and new
all_rows = existing_rows + new_rows

# Write full CSV with unified header
with open(salon_leads_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=final_header)
    writer.writeheader()
    writer.writerows(all_rows)

print(f"Added {len(new_rows)} new leads to salon_leads_csv (total {len(all_rows)}).")