#!/usr/bin/env python3
"""
Send outreach emails via gog (Gmail) and update lead status.
"""

import argparse
import json
import subprocess
import sys
import time

def load_emails(emails_file):
    with open(emails_file, 'r') as f:
        return json.load(f)

def load_leads(leads_file):
    with open(leads_file, 'r') as f:
        return json.load(f)

def update_lead_status(leads_file, lead_id, new_status, notes=None):
    """Update a lead's status in the leads JSON file."""
    with open(leads_file, 'r') as f:
        leads = json.load(f)

    for lead in leads:
        if lead.get('id') == lead_id or lead.get('name', '').lower().replace(' ', '-') == lead_id:
            lead['status'] = new_status
            if notes:
                lead['notes'] = notes
            lead['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
            break

    with open(leads_file, 'w') as f:
        json.dump(leads, f, indent=2)

def send_email_gog(to_email, subject, body, dry_run=False):
    """Send email using gog CLI."""
    if dry_run:
        print(f"[DRY RUN] Would send email to: {to_email}")
        print(f"  Subject: {subject}")
        print(f"  Body: {body[:100]}...")
        return True, "dry-run"

    # Use gog gmail send with stdin for body
    cmd = [
        'gog', 'gmail', 'send',
        '--account', 'justiceforanything@gmail.com',
        '--to', to_email,
        '--subject', subject,
        '--body-file', '-'
    ]

    try:
        result = subprocess.run(
            cmd,
            input=body.encode(),
            capture_output=True,
            timeout=30
        )
        if result.returncode == 0:
            # Extract message ID from output if available
            output = result.stdout.decode()
            return True, output
        else:
            error = result.stderr.decode()
            print(f"Error sending to {to_email}: {error}", file=sys.stderr)
            return False, error
    except subprocess.TimeoutExpired:
        print(f"Timeout sending to {to_email}", file=sys.stderr)
        return False, "timeout"
    except Exception as e:
        print(f"Exception sending to {to_email}: {e}", file=sys.stderr)
        return False, str(e)

def main():
    parser = argparse.ArgumentParser(description='Send outreach emails via Gmail.')
    parser.add_argument('--emails', required=True, help='Emails JSON from draft-outreach')
    parser.add_argument('--leads', help='Leads JSON file to update (optional but recommended)')
    parser.add_argument('--dry-run', action='store_true', help='Preview without sending')
    parser.add_argument('--batch-size', type=int, default=25, help='Emails per batch')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between emails (seconds)')
    args = parser.parse_args()

    emails = load_emails(args.emails)

    if args.dry_run:
        print(f"DRY RUN: {len(emails)} emails would be sent.\n")
    else:
        print(f"Preparing to send {len(emails)} emails...\n")

    # Load leads if updating status
    leads = None
    if args.leads:
        leads = load_leads(args.leads)

    sent_count = 0
    fail_count = 0

    for i, email in enumerate(emails, 1):
        print(f"[{i}/{len(emails)}] Sending to {email['to']}...")

        success, msg = send_email_gog(email['to'], email['subject'], email['body'], args.dry_run)

        if success or args.dry_run:
            sent_count += 1
            # Update lead status if we have leads file
            if leads and email.get('lead_id'):
                update_lead_status(args.leads, email['lead_id'], 'emailed', f"Sent: {email['template']}")
        else:
            fail_count += 1

        # Rate limiting
        if not args.dry_run and i < len(emails):
            time.sleep(args.delay)

    print(f"\n✓ Complete!")
    print(f"  Sent: {sent_count}")
    print(f"  Failed: {fail_count}")

    if args.leads and sent_count > 0:
        print(f"\nLead statuses updated in {args.leads}")

    if not args.dry_run and fail_count > 0:
        print("\n⚠️  Some emails failed. Consider retrying after fixing issues.")

if __name__ == '__main__':
    main()
