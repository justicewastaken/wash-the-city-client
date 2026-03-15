#!/usr/bin/env python3
"""
Generate initial outreach emails for any leads in leads_master.json that
have an email address but do not yet have an entry in salon_emails_remaining.json.
Append new emails to salon_emails_remaining.json.
"""

import json, os, sys
from pathlib import Path

workspace = Path('/root/.openclaw/workspace')
master_json = workspace / 'leads_master.json'
remaining_json = workspace / 'salon_emails_remaining.json'

# Load configuration (set these environment variables)
PORTFOLIO_URL = os.environ.get('PORTFOLIO_URL', 'https://justicewastaken.github.io/forward-media/')
YOUR_PHONE = os.environ.get('YOUR_PHONE', '715-308-7949')

# Initial email template (booking-platform-aware)
TEMPLATE = """Subject: UW-Eau Claire student building salon websites

Hey {owner_name},

I'm a UW-Eau Claire student learning web dev and building my portfolio. I was looking at {business_name} in {city} and noticed you're using {booking_platform} for appointments. That's fine for bookings, but you don't have a proper website to showcase your work and tell your story.

I can create a custom site for you at a rate well below an agency's. I'm not a big shop—just me, trying to get real experience.

If you're up for it, I'll throw together a quick mockup for you to review—no cost, no pressure. Just let me know what you think.

Best,
Justice
{YOUR_PHONE}
{PORTFOLIO_URL}"""

def substitute(template, context):
    for key, value in context.items():
        placeholder = '{' + key + '}'
        template = template.replace(placeholder, str(value) if value else '')
    return template

# Load data
try:
    with open(master_json, 'r', encoding='utf-8') as f:
        master = json.load(f)
except FileNotFoundError:
    print(f"Error: {master_json} not found. Run refresh_master_from_enriched first.", file=sys.stderr)
    sys.exit(1)

if remaining_json.exists():
    with open(remaining_json, 'r', encoding='utf-8') as f:
        remaining = json.load(f)
else:
    remaining = []

# Build set of lead_ids already in remaining
sent_ids = {email['lead_id'] for email in remaining if email.get('lead_id')}

new_emails = []
for lead in master:
    lid = lead['id']
    if lid in sent_ids:
        continue
    if not lead.get('email'):
        continue
    # Skip leads that are already contacted/closed
    if lead.get('status') in ('emailed', 'sent-payment', 'paid', 'closed-lost'):
        continue
    # Build context
    owner_name = lead.get('owner_first_name') or 'there'
    city = lead.get('city') or 'your area'
    booking_platform = lead.get('booking_platform') or 'a booking system'
    business = lead.get('business_name') or lead.get('name') or 'your salon'
    body = substitute(TEMPLATE, {
        'owner_name': owner_name,
        'city': city,
        'booking_platform': booking_platform,
        'business_name': business,
        'YOUR_PHONE': YOUR_PHONE,
        'PORTFOLIO_URL': PORTFOLIO_URL
    })
    # Split subject: first line contains "Subject: ..."
    lines = body.split('\n')
    first = lines[0].strip()
    if first.lower().startswith('subject:'):
        subject = first[8:].strip()
        body = '\n'.join(lines[1:]).strip()
    else:
        subject = first
        body = '\n'.join(lines[1:]).strip()
    email = {
        'to': lead['email'],
        'subject': subject,
        'body': body,
        'lead_name': business,
        'lead_id': lid,
        'template': 'initial'
    }
    new_emails.append(email)

if not new_emails:
    print("No new emails to generate.")
    sys.exit(0)

# Append to remaining
remaining.extend(new_emails)
with open(remaining_json, 'w', encoding='utf-8') as f:
    json.dump(remaining, f, indent=2, ensure_ascii=False)

print(f"Added {len(new_emails)} new emails to salon_emails_remaining.json.")
print("New leads:")
for em in new_emails:
    print(f" - {em['lead_name']} ({em['to']})")