#!/usr/bin/env python3
"""
Schedule follow-up reminders in Google Calendar.
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta

def load_leads(leads_file):
    with open(leads_file, 'r') as f:
        return json.load(f)

def create_calendar_event(lead_name, days_from_now, calendar_id='primary', description=None):
    """Create a follow-up reminder event in Google Calendar using gog."""
    event_date = datetime.now() + timedelta(days=days_from_now)
    # Set time for 10 AM local
    event_start = event_date.replace(hour=10, minute=0, second=0, microsecond=0)
    event_end = event_start + timedelta(hours=1)

    # ISO format for gog
    start_iso = event_start.isoformat()
    end_iso = event_end.isoformat()

    summary = f"Follow up: {lead_name} (website lead)"
    if not description:
        description = f"Send follow-up email to {lead_name}.\n\nLead status: check notes."

    # Use gog calendar create
    cmd = [
        'gog', 'calendar', 'create', calendar_id,
        '--summary', summary,
        '--from', start_iso,
        '--to', end_iso,
        '--description', description
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            # Parse event ID from output
            return True, result.stdout
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)

def main():
    parser = argparse.ArgumentParser(description='Schedule follow-up reminders in Google Calendar.')
    parser.add_argument('--leads', required=True, help='Leads JSON file')
    parser.add_argument('--days', default='3,7,14', help='Days after initial to schedule reminders (comma-separated)')
    parser.add_argument('--calendar', default='primary', help='Calendar ID')
    parser.add_argument('--status-filter', default='emailed,responded', help='Only schedule for these statuses')
    parser.add_argument('--dry-run', action='store_true', help='Preview without creating events')
    args = parser.parse_args()

    leads = load_leads(args.leads)
    days_list = [int(d.strip()) for d in args.days.split(',')]
    statuses = args.status_filter.split(',')

    # Filter leads
    target_leads = [l for l in leads if l.get('status') in statuses and l.get('name')]

    if not target_leads:
        print("No leads match the criteria.")
        return

    print(f"Scheduling follow-ups for {len(target_leads)} leads...")
    if args.dry_run:
        print("(DRY RUN - no events will be created)\n")

    created = 0
    errors = 0

    for lead in target_leads:
        name = lead.get('name')
        for days in days_list:
            if args.dry_run:
                print(f"[DRY RUN] Would create event: Follow up: {name} in {days} days")
            else:
                success, msg = create_calendar_event(name, days, args.calendar)
                if success:
                    print(f"✓ Scheduled {days}-day follow-up for {name}")
                    created += 1
                else:
                    print(f"✗ Error for {name} ({days}d): {msg}", file=sys.stderr)
                    errors += 1
                time.sleep(1)  # Rate limit

    if not args.dry_run:
        print(f"\n✓ Created {created} events")
        if errors:
            print(f"⚠️  {errors} errors")

    print("\nDone.")

if __name__ == '__main__':
    main()
