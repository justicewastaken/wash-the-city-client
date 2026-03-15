#!/usr/bin/env python3
"""
Notify when leads reply to outreach emails.
Checks Gmail, filters auto-replies, sends Telegram alerts.
"""

import os
import json
import subprocess
import re
from datetime import datetime

# Configuration
STATE_FILE = '/root/.openclaw/workspace/notify_replies_state.json'
GOG_PASSWORD = 'opensesame'
CHECK_OLDER_THAN_HOURS = 1  # only process messages from the last X hours (since we sent)
# Target senders we emailed (domains) - will be auto-populated from leads file
TARGET_DOMAINS = set()

def load_state():
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'seen_message_ids': [], 'last_run': None}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def load_target_domains_from_leads():
    """Load email domains from our leads file to filter replies."""
    leads_path = '/root/.openclaw/workspace/salon_leads_enriched.csv'
    domains = set()
    try:
        with open(leads_path, 'r', encoding='utf-8') as f:
            next(f)  # skip header
            for line in f:
                parts = line.split(',')
                if len(parts) >= 7:
                    email = parts[6].strip().lower()
                    if '@' in email:
                        domain = email.split('@')[1].strip('"')
                        if domain:
                            domains.add(domain)
    except Exception as e:
        print(f"Could not load leads: {e}")
    return domains

def is_auto_reply(msg):
    """Heuristically detect automated replies."""
    # Check subject for typical auto-reply phrases
    subject = msg.get('subject', '').lower()
    auto_phrases = [
        'auto', 'autoreply', 'automatic', 'out of office', 'ooo', 'vacation',
        'do not reply', 'noreply', 'no-reply', 'mail delivery', 'undeliverable',
        'delivery status', 'bounce', 'returned mail', 'confirmation', 'receipt',
        'appointment confirmed', 'booking confirmed'
    ]
    for phrase in auto_phrases:
        if phrase in subject:
            return True
    
    # Sender address patterns
    sender = msg.get('from', '').lower()
    auto_senders = ['no-reply', 'noreply', 'postmaster', 'mailer-daemon', 'daemon', 'support@', 'help@', 'info@vagaro.com', 'notifications@', 'confirmations@', 'appointments@', 'no-reply@']
    for pattern in auto_senders:
        if pattern in sender:
            return True
    
    return False

def query_gmail():
    """Fetch recent incoming emails (since we sent)."""
    query = f'newer_than:{CHECK_OLDER_THAN_HOURS}h -from:me'
    cmd = ['gog', 'gmail', 'search', query, '-j', '--results-only']
    env = os.environ.copy()
    env['GOG_KEYRING_PASSWORD'] = GOG_PASSWORD
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)
        if result.returncode != 0:
            print(f"Gmail search error: {result.stderr}")
            return []
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error querying Gmail: {e}")
        return []

def send_telegram_alert(text):
    """Send a Telegram message via OpenClaw."""
    try:
        subprocess.run([
            'openclaw', 'message', 'send',
            '--target', '5606165796',
            '--message', text
        ], timeout=10)
        return True
    except Exception as e:
        print(f"Failed to send Telegram: {e}")
        return False

def main():
    global TARGET_DOMAINS
    TARGET_DOMAINS = load_target_domains_from_leads()
    print(f"[{datetime.now().isoformat()}] Notifier starting. Target domains: {len(TARGET_DOMAINS)}")
    
    state = load_state()
    messages = query_gmail()
    new_replies = []
    
    for msg in messages:
        msg_id = msg.get('id') or msg.get('message_id')
        if not msg_id or msg_id in state['seen_message_ids']:
            continue
        
        sender = msg.get('from', '').lower()
        subject = msg.get('subject', '')
        
        # Must be from one of our target domains OR reply to our email subject
        is_target = any(domain in sender for domain in TARGET_DOMAINS)
        is_our_subject = 'UW-Eau Claire student building salon websites' in subject
        
        if (is_target or is_our_subject) and not is_auto_reply(msg):
            new_replies.append(msg)
            state['seen_message_ids'].append(msg_id)
    
    state['last_run'] = datetime.now().isoformat()
    save_state(state)
    
    if new_replies:
        print(f"Found {len(new_replies)} new replies!")
        for msg in new_replies:
            sender = msg.get('from', 'Unknown')
            subject = msg.get('subject', 'No subject')
            snippet = msg.get('snippet', '')[:150]
            alert = (
                f"📬 New reply from lead!\n"
                f"From: {sender}\n"
                f"Subject: {subject}\n"
                f"Preview: {snippet}..."
            )
            send_telegram_alert(alert)
            print(f"Alert sent for {sender}")
    else:
        print("No new replies.")
    
    return 0

if __name__ == '__main__':
    exit(main())
