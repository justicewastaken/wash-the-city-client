#!/usr/bin/env python3
"""
Recursive Improver — continuous optimization for website-sales pipeline.

Runs twice daily; analyzes performance; makes small adjustments; logs everything.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path('/root/.openclaw/workspace')
LEADS_MASTER = WORKSPACE / 'leads_master.json'
UNSENT_EMAILS = WORKSPACE / 'salon_emails_remaining.json'
CONFIG_FILE = WORKSPACE / 'improver_config.json'
IMPROVEMENTS_LOG = WORKSPACE / '.learnings' / 'IMPROVEMENTS.md'
PIPELINE_LOGS = WORKSPACE / 'pipeline_summary.log'  # daily summary

# Default configuration
DEFAULT_CONFIG = {
    'auto_apply': False,
    'max_batch_size': 30,
    'min_batch_size': 5,
    'template_variants': ['default'],  # could have v1, v2, etc.
    'metrics_window_days': 3,
    'reorder_by_performance': True,
    'adjust_batch_size': True
}

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            cfg = json.load(f)
        return {**DEFAULT_CONFIG, **cfg}
    else:
        return DEFAULT_CONFIG.copy()

def load_leads():
    with open(LEADS_MASTER, 'r') as f:
        return json.load(f)

def load_unsent():
    if UNSENT_EMAILS.exists():
        with open(UNSENT_EMAILS, 'r') as f:
            return json.load(f)
    return []

def save_unsent(emails):
    with open(UNSENT_EMAILS, 'w') as f:
        json.dump(emails, f, indent=2, ensure_ascii=False)

def parse_send_logs(days=3):
    """Extract sent counts and failures from pipeline send logs within window."""
    from glob import glob
    cutoff = datetime.now() - timedelta(days=days)
    totals = {'sent': 0, 'failed': 0, 'batches': []}
    pattern = str(WORKSPACE / 'pipeline_send_*.log')
    for logfile in glob(pattern):
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(logfile))
            if mtime < cutoff:
                continue
            with open(logfile, 'r') as f:
                content = f.read()
            # Extract Sent/Failed lines
            sent = 0; failed = 0
            for line in content.splitlines():
                if re.search(r'Sent:\s*(\d+)', line):
                    sent = int(re.search(r'Sent:\s*(\d+)', line).group(1))
                if re.search(r'Failed:\s*(\d+)', line):
                    failed = int(re.search(r'Failed:\s*(\d+)', line).group(1))
            totals['sent'] += sent
            totals['failed'] += failed
            totals['batches'].append({'file': logfile, 'sent': sent, 'failed': failed})
        except Exception as e:
            pass
    return totals

def get_performance_by_segment(leads):
    """Group leads by segment and compute reply rates."""
    segments = {
        'by_city': defaultdict(lambda: {'sent': 0, 'replied': 0}),
        'by_platform': defaultdict(lambda: {'sent': 0, 'replied': 0}),
    }
    for lead in leads:
        status = lead.get('status', 'prospect')
        city = lead.get('city', 'unknown')
        platform = lead.get('booking_platform', 'none')
        # Only count leads that have been emailed (status in emailed, responded, sent-payment, paid, closed-lost)
        if status in ('emailed', 'responded', 'sent-payment', 'paid', 'closed-lost'):
            segments['by_city'][city]['sent'] += 1
            if status in ('responded', 'sent-payment', 'paid'):
                segments['by_city'][city]['replied'] += 1
            segments['by_platform'][platform]['sent'] += 1
            if status in ('responded', 'sent-payment', 'paid'):
                segments['by_platform'][platform]['replied'] += 1
    # Compute rates
    rates = {}
    for seg_name, data in segments.items():
        rates[seg_name] = {}
        for key, counts in data.items():
            if counts['sent'] > 0:
                rates[seg_name][key] = counts['replied'] / counts['sent']
            else:
                rates[seg_name][key] = 0.0
    return rates, segments

def suggest_adjustments(leads, unsent, config, metrics):
    """Return a list of suggested changes."""
    suggestions = []
    rates, segments = get_performance_by_segment(leads)

    # 1. Prioritize unsent leads: move high-performing segments to front
    if config['reorder_by_performance'] and unsent:
        # Compute a score for each unsent lead based on segment reply rates
        scored = []
        for i, email in enumerate(unsent):
            lead_id = email.get('lead_id')
            lead = next((l for l in leads if l['id'] == lead_id), None)
            if not lead:
                score = 0.5
            else:
                city = lead.get('city', 'unknown')
                platform = lead.get('booking_platform', 'none')
                city_rate = rates['by_city'].get(city, 0.0)
                platform_rate = rates['by_platform'].get(platform, 0.0)
                score = (city_rate + platform_rate) / 2 if (city_rate and platform_rate) else max(city_rate, platform_rate)
            scored.append((score, i, email))
        # Check if reordering would change order significantly
        scored.sort(key=lambda x: x[0], reverse=True)
        new_order = [e for _, _, e in scored]
        old_order = unsent
        if [e['lead_id'] for e in new_order] != [e['lead_id'] for e in old_order]:
            suggestions.append({
                'type': 'reorder_unsent',
                'desc': f'Reorder unsent emails by segment performance (top: {new_order[0]["lead_name"] if new_order else "none"})',
                'old': unsent,
                'new': new_order
            })

    # 2. Adjust batch size based on recent failure rate
    if config['adjust_batch_size']:
        total_sent = metrics['sent']
        total_failed = metrics['failed']
        fail_rate = total_failed / total_sent if total_sent > 0 else 0
        current_batch = min(config['max_batch_size'], len(unsent))
        if fail_rate > 0.1:
            # Too many failures? Reduce batch size to be safe
            new_batch = max(config['min_batch_size'], int(current_batch * 0.7))
            if new_batch != current_batch:
                suggestions.append({
                    'type': 'adjust_batch_size',
                    'desc': f'High failure rate ({fail_rate:.1%}); reduce batch size from {current_batch} to {new_batch}',
                    'batch_size': new_batch
                })
        elif fail_rate == 0 and total_sent > 20:
            # Good performance, can increase slowly
            new_batch = min(config['max_batch_size'], int(current_batch * 1.2))
            if new_batch != current_batch:
                suggestions.append({
                    'type': 'adjust_batch_size',
                    'desc': f'Zero failures; increase batch size from {current_batch} to {new_batch}',
                    'batch_size': new_batch
                })

    # 3. (Future) Switch template variants if multiple exist
    # Not implemented yet

    return suggestions

def log_improvement(suggestions, applied):
    IMPROVEMENTS_LOG.parent.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(IMPROVEMENTS_LOG, 'a') as f:
        f.write(f"## {timestamp}\n\n")
        f.write(f"**Auto-apply:** {applied}\n\n")
        f.write("**Suggestions:**\n")
        if not suggestions:
            f.write("- No changes recommended.\n\n")
        else:
            for s in suggestions:
                f.write(f"- [{s['type']}] {s['desc']}\n")
            if applied:
                f.write("\n**Applied changes:**\n")
                for s in suggestions:
                    if s['type'] == 'reorder_unsent':
                        f.write(f"- Reordered unsent emails (new top: {s['new'][0]['lead_name']})\n")
                    elif s['type'] == 'adjust_batch_size':
                        f.write(f"- Adjusted batch size to {s['batch_size']}\n")
            else:
                f.write("\n*(dry-run — changes not applied)*\n")
        f.write("---\n\n")

def apply_changes(suggestions, unsent, config):
    """Modify files in place according to suggestions."""
    changed = False
    for s in suggestions:
        if s['type'] == 'reorder_unsent':
            save_unsent(s['new'])
            changed = True
        elif s['type'] == 'adjust_batch_size':
            config['max_batch_size'] = s['batch_size']
            config['min_batch_size'] = max(5, int(s['batch_size'] * 0.5))
            # Save config
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            changed = True
    return changed

def main():
    parser = argparse.ArgumentParser(description='Recursive Improver for website-sales pipeline')
    parser.add_argument('--auto-apply', action='store_true', help='Actually modify files (default: dry-run)')
    parser.add_argument('--dry-run', action='store_true', help='Preview without applying')
    args = parser.parse_args()

    config = load_config()
    leads = load_leads()
    unsent = load_unsent()
    metrics = parse_send_logs(days=config['metrics_window_days'])

    suggestions = suggest_adjustments(leads, unsent, config, metrics)

    if args.auto_apply:
        changed = apply_changes(suggestions, unsent, config)
        log_improvement(suggestions, applied=True)
        print(f"Improver: Applied {len(suggestions)} changes.")
        if changed:
            print("Files updated.")
        else:
            print("No changes made.")
    else:
        log_improvement(suggestions, applied=False)
        print(f"Improver: Generated {len(suggestions)} suggestions (dry-run).")
        for s in suggestions:
            print(f" - {s['type']}: {s['desc']}")

if __name__ == '__main__':
    main()