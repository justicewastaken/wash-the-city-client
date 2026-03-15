#!/usr/bin/env python3
"""
Merge enriched leads from salon_leads_enriched.csv into leads_master.json.
Deduplicates by business name slug.
"""

import csv, json, sys
from datetime import datetime
from pathlib import Path

workspace = Path('/root/.openclaw/workspace')
enriched_csv = workspace / 'salon_leads_enriched.csv'
master_json = workspace / 'leads_master.json'

def slugify(name):
    return name.strip().lower().replace(' ', '-')

# Load master into dict by id, plus list
master = {}
master_list = []
if master_json.exists():
    with open(master_json, 'r', encoding='utf-8') as f:
        master_list = json.load(f)
        for lead in master_list:
            master[lead['id']] = lead

# Load enriched CSV
new_count = 0
try:
    with open(enriched_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            business_name = row.get('business_name', '').strip()
            if not business_name:
                continue
            lead_id = slugify(business_name)
            if lead_id in master:
                continue  # skip duplicate
            lead = {
                'id': lead_id,
                'business_name': business_name,
                'name': business_name,
                'website': row.get('website', '').strip(),
                'phone': row.get('phone', '').strip(),
                'has_website': row.get('has_website', '').strip().lower() == 'true',
                'booking_platform': row.get('booking_platform', '').strip(),
                'owner_first_name': row.get('owner_first_name', '').strip(),
                'email': row.get('email', '').strip(),
                'notes': row.get('notes', '').strip(),
                'city': row.get('city', '').strip() or None,
                'status': 'prospect',
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            master[lead_id] = lead
            master_list.append(lead)
            new_count += 1
except FileNotFoundError:
    print(f"Error: {enriched_csv} not found. Run enrichment first.", file=sys.stderr)
    sys.exit(1)

# Save master
with open(master_json, 'w', encoding='utf-8') as f:
    json.dump(master_list, f, indent=2, ensure_ascii=False)

print(f"Merged {new_count} new leads into leads_master.json (total: {len(master_list)})")