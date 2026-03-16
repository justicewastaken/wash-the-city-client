#!/usr/bin/env python3
"""Send batch emails via SMTP directly (no gog keyring issues)."""
import json
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path
import sys
import time

def load_config(config_path='.email_config.json'):
    with open(config_path, 'r') as f:
        return json.load(f)

def send_email_smtp(to_email, subject, body, config):
    msg = EmailMessage()
    msg['From'] = config['username']
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP(config['smtp_host'], config['smtp_port']) as server:
        server.starttls(context=context)
        server.login(config['username'], config['password'])
        server.send_message(msg)

def update_lead_status(leads_file, lead_id, new_status, notes=None):
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

def main():
    if len(sys.argv) < 2:
        print("Usage: send_batch_smtp.py <batch_emails_json> [leads_master_json]")
        sys.exit(1)

    batch_file = sys.argv[1]
    leads_file = sys.argv[2] if len(sys.argv) > 2 else 'leads_master.json'

    config = load_config()
    with open(batch_file, 'r') as f:
        emails = json.load(f)

    print(f"Sending {len(emails)} emails via SMTP...")
    sent = 0
    for item in emails:
        to_email = item['to']
        subject = item['subject']
        body = item['body']
        lead_id = item.get('lead_id', to_email)

        try:
            send_email_smtp(to_email, subject, body, config)
            print(f"✓ Sent to {to_email}")
            update_lead_status(leads_file, lead_id, 'emailed', f"Sent via SMTP on {time.strftime('%Y-%m-%d')}")
            sent += 1
        except Exception as e:
            print(f"✗ Failed to send to {to_email}: {e}")

    print(f"\nSent: {sent}/{len(emails)}")

if __name__ == '__main__':
    main()
