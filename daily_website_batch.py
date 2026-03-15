#!/usr/bin/env python3
"""
Daily batch sender for website-sales outreach.

Usage:
  ./daily_website_batch.py [--batch-size N] [--dry-run] [--send]

If --send is omitted, runs in dry-run mode (preview only).

This script:
  1. Reads unsent emails from salon_emails_remaining.json
  2. Selects up to --batch-size emails whose leads are not already 'emailed' in leads_master.json
  3. Sends them via website-sales send-emails
  4. Updates leads_master.json and salon_emails_remaining.json
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

WORKSPACE = os.path.dirname(os.path.abspath(__file__))

LEADS_MASTER = os.path.join(WORKSPACE, 'leads_master.json')
UNSENT_EMAILS = os.path.join(WORKSPACE, 'salon_emails_remaining.json')
TEMP_BATCH = os.path.join(WORKSPACE, 'temp_batch_emails.json')
SEND_SCRIPT = os.path.join(WORKSPACE, 'skills/website-sales/scripts/send_emails.py')

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def ensure_files():
    for p in [LEADS_MASTER, UNSENT_EMAILS, SEND_SCRIPT]:
        if not os.path.exists(p):
            print(f"Error: required file missing: {p}", file=sys.stderr)
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Daily batch sender for website-sales.')
    parser.add_argument('--batch-size', type=int, default=20, help='Number of emails to send today (default: 20)')
    parser.add_argument('--dry-run', action='store_true', help='Preview without sending (default action is dry-run)')
    parser.add_argument('--send', action='store_true', help='Actually send emails')
    parser.add_argument('--min-delay', type=float, default=2.5, help='Delay between emails in seconds (default: 2.5)')
    args = parser.parse_args()

    ensure_files()

    # Load leads master and index by id
    leads_list = load_json(LEADS_MASTER)
    leads_by_id = {lead['id']: lead for lead in leads_list}

    # Load unsent emails
    unsent_emails = load_json(UNSENT_EMAILS)

    # Build today's batch: take first N emails whose lead status is not 'emailed'/'sent-payment'/'paid'/'closed-lost'
    batch = []
    remaining = []
    used_lead_ids = set()
    for email in unsent_emails:
        lead_id = email.get('lead_id')
        if not lead_id:
            remaining.append(email)
            continue
        lead = leads_by_id.get(lead_id)
        if lead is None:
            # Lead not in master? Could add placeholder to avoid crash in send_emails
            lead = {
                'id': lead_id,
                'business_name': email.get('lead_name', ''),
                'name': email.get('lead_name', ''),
                'status': 'prospect',
                'email': email.get('to', '')
            }
            leads_by_id[lead_id] = lead
            leads_list.append(lead)
        if lead.get('status') in ('emailed', 'sent-payment', 'paid', 'closed-lost'):
            # Already processed; drop from unsent (do not add back to remaining)
            continue
        if lead_id in used_lead_ids:
            # Duplicate lead in same batch? skip second occurrence
            continue
        if len(batch) < args.batch_size:
            batch.append(email)
            used_lead_ids.add(lead_id)
        else:
            remaining.append(email)

    if not batch:
        print("No emails to send today. All caught up or all leads already processed.")
        sys.exit(0)

    print(f"Today's batch: {len(batch)} emails to send.")
    for i, em in enumerate(batch, 1):
        print(f"  {i}. {em['lead_name']} ({em['to']})")

    if not args.send:
        print("\nDRY RUN: Not sending. Use --send to actually send these emails.")
        print("\nWould update lead statuses in leads_master.json to 'emailed' for:")
        for em in batch:
            lead_id = em.get('lead_id')
            lead = leads_by_id.get(lead_id)
            if lead:
                print(f"  - {lead.get('business_name', lead_id)}")
        sys.exit(0)

    # Write temporary batch file
    save_json(TEMP_BATCH, batch)

    # Call send_emails.py
    send_cmd = [
        sys.executable,
        SEND_SCRIPT,
        '--emails', TEMP_BATCH,
        '--leads', LEADS_MASTER,
        '--delay', str(args.min_delay)
    ]
    print(f"\nRunning: {' '.join(send_cmd)}")
    result = subprocess.run(send_cmd)
    if result.returncode != 0:
        print(f"Error: send_emails failed with exit code {result.returncode}", file=sys.stderr)
        sys.exit(1)

    # After sending, update leads_master.json (send_emails already did) and unsent file
    # Reload leads to get any new modifications
    updated_leads = load_json(LEADS_MASTER)
    leads_by_id = {lead['id']: lead for lead in updated_leads}
    save_json(LEADS_MASTER, updated_leads)

    # Rebuild remaining: all emails not in batch, plus those skipped because already processed
    # We'll take original unsent list and remove any email whose lead_id is in used_lead_ids
    new_remaining = []
    for email in unsent_emails:
        lid = email.get('lead_id')
        if lid and lid in used_lead_ids:
            # This was sent today; skip adding to remaining
            continue
        # Otherwise keep it for future days
        new_remaining.append(email)

    save_json(UNSENT_EMAILS, new_remaining)

    # Cleanup temp batch file
    if os.path.exists(TEMP_BATCH):
        os.remove(TEMP_BATCH)

    print(f"\n✓ Batch complete.")
    print(f"  Sent: {len(batch)}")
    print(f"  Remaining unsent: {len(new_remaining)}")
    print(f"  Leads updated in {LEADS_MASTER}")
    print(f"  Next: run this script again tomorrow to send more.")

if __name__ == '__main__':
    main()