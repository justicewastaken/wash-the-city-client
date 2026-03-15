#!/usr/bin/env python3
"""
Create a master leads file from salon_leads_enriched.csv
with deduplication and slugified IDs matching draft_outreach.py.
"""

import csv
import json
import re
import sys
from datetime import datetime

CSV_PATH = '/root/.openclaw/workspace/salon_leads_enriched.csv'
OUTPUT_PATH = '/root/.openclaw/workspace/leads_master.json'

def slugify(name):
    """Match draft_outreach: lower + replace spaces with hyphens."""
    return name.strip().lower().replace(' ', '-')

def main():
    leads = {}
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            business_name = row.get('business_name', '').strip()
            if not business_name:
                continue
            lead_id = slugify(business_name)
            # Deduplicate: keep first occurrence; later duplicates get skipped
            if lead_id in leads:
                continue
            lead = {
                'id': lead_id,
                'business_name': business_name,
                'name': business_name,  # compatibility
                'website': row.get('website', '').strip(),
                'phone': row.get('phone', '').strip(),
                'has_website': row.get('has_website', '').strip().lower() == 'true',
                'booking_platform': row.get('booking_platform', '').strip(),
                'owner_first_name': row.get('owner_first_name', '').strip(),
                'email': row.get('email', '').strip(),
                'notes': row.get('notes', '').strip(),
                'city': None,  # will default to 'your area' in emails
                'status': 'prospect',
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            leads[lead_id] = lead

    lead_list = list(leads.values())
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(lead_list, f, indent=2, ensure_ascii=False)

    print(f"✓ Created {OUTPUT_PATH} with {len(lead_list)} unique leads.")
    print("  Note: city field is empty; email personalization will use 'your area'.")

if __name__ == '__main__':
    main()