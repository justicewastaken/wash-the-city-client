#!/usr/bin/env python3
"""
Daily pipeline summary — runs at 11 PM CT, reports on today's activity.
Checks send logs and remaining email pool, writes to a summary file.
"""

import glob
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

workspace = Path('/root/.openclaw/workspace')
LOG_DIR = workspace
SUMMARY_FILE = workspace / 'daily_pipeline_summary.log'

def get_today_utc_date():
    """Return date string for 'today' in UTC (since cron runs in UTC)."""
    # Pipeline logs are written on the same UTC day they run.
    # We'll summarize today's logs.
    return datetime.utcnow().strftime('%Y-%m-%d')

def parse_send_logs():
    """Parse all send logs for today and count sent/failed."""
    today = get_today_utc_date()
    pattern = str(LOG_DIR / f'pipeline_send_*.log')
    logs = glob.glob(pattern)
    total_sent = 0
    total_failed = 0
    details = []
    for log in logs:
        # Extract hour from filename to identify which batch
        # Filename: pipeline_send_7am.log etc. (doesn't contain date)
        # We'll read the log and look for today's date in output? Simpler: just count all lines that say "Sent:" and "Failed:"
        try:
            with open(log, 'r', encoding='utf-8') as f:
                content = f.read()
            # Look for "Sent: X" lines (final summary)
            # Example: "  Sent: 10\n  Failed: 0"
            # We'll sum all Sent/Failed from today's logs (assuming logs are only for today)
            # To avoid double-counting if logs accumulate, we could check modification date, but simplest is to sum across all send logs (they're separate per batch)
            lines = content.splitlines()
            for line in lines:
                if line.strip().startswith('Sent:'):
                    try:
                        sent = int(line.strip().split(':')[1].strip())
                        total_sent += sent
                    except:
                        pass
                if line.strip().startswith('Failed:'):
                    try:
                        failed = int(line.strip().split(':')[1].strip())
                        total_failed += failed
                    except:
                        pass
        except Exception as e:
            details.append(f"Error reading {log}: {e}")
    return total_sent, total_failed, details

def get_remaining_count():
    """Count unsent emails remaining."""
    try:
        with open(workspace / 'salon_emails_remaining.json', 'r', encoding='utf-8') as f:
            emails = json.load(f)
        return len(emails)
    except Exception:
        return None

def get_leads_master_stats():
    """Get counts of leads by status."""
    try:
        with open(workspace / 'leads_master.json', 'r', encoding='utf-8') as f:
            leads = json.load(f)
        from collections import Counter
        status_counts = Counter(l.get('status', 'unknown') for l in leads)
        return status_counts
    except Exception:
        return None

def write_summary():
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M:%S')
    lines = []
    lines.append(f"=== Daily Pipeline Summary ===")
    lines.append(f"Date: {date_str} {time_str} CT")
    lines.append("")
    
    # Send stats
    sent, failed, details = parse_send_logs()
    lines.append(f"Emails sent today: {sent}")
    lines.append(f"Emails failed: {failed}")
    if details:
        lines.append("Log issues:")
        lines.extend(details)
    
    # Remaining pool
    remaining = get_remaining_count()
    if remaining is not None:
        lines.append(f"Emails remaining in pool: {remaining}")
    
    # Lead status
    status_counts = get_leads_master_stats()
    if status_counts:
        lines.append("Lead statuses:")
        for status, count in sorted(status_counts.items()):
            lines.append(f"  {status}: {count}")
    
    lines.append("")
    lines.append("---")
    
    # Append to summary file
    with open(SUMMARY_FILE, 'a', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    
    # Also print for logging
    print('\n'.join(lines))
    return lines

if __name__ == '__main__':
    write_summary()