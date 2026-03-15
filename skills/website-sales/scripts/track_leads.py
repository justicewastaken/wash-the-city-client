#!/usr/bin/env python3
"""
Update lead status and notes in tracking file.
"""

import argparse
import json
import sys
import time

def load_leads(leads_file):
    with open(leads_file, 'r') as f:
        return json.load(f)

def save_leads(leads_file, leads):
    with open(leads_file, 'w') as f:
        json.dump(leads, f, indent=2)

def find_lead(leads, lead_id):
    """Find lead by id or normalized name."""
    for lead in leads:
        if lead.get('id') == lead_id:
            return lead
        # Also try normalized name match
        name_match = lead.get('name', '').lower().replace(' ', '-')
        if name_match == lead_id.lower():
            return lead
    return None

def main():
    parser = argparse.ArgumentParser(description='Update lead status in tracking.')
    parser.add_argument('--lead-id', required=True, help='Lead ID or business name')
    parser.add_argument('--status', required=True, choices=['prospect', 'contacted', 'responded', 'sent-payment', 'paid', 'closed-lost'], help='New status')
    parser.add_argument('--notes', help='Optional notes')
    parser.add_argument('--leads-file', default='leads.json', help='Leads JSON file')
    args = parser.parse_args()

    leads = load_leads(args.leads_file)
    lead = find_lead(leads, args.lead_id)

    if not lead:
        print(f"Error: Lead '{args.lead_id}' not found in {args.leads_file}", file=sys.stderr)
        sys.exit(1)

    old_status = lead.get('status', 'unknown')
    lead['status'] = args.status
    if args.notes:
        lead['notes'] = args.notes
    lead['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')

    save_leads(args.leads_file, leads)

    print(f"✓ Updated '{lead.get('name')}':")
    print(f"  Status: {old_status} → {args.status}")
    if args.notes:
        print(f"  Notes: {args.notes}")

if __name__ == '__main__':
    main()
