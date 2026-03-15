#!/usr/bin/env python3
"""
Website Sales Pipeline — daily automation for local web design outreach.

Runs full pipeline: scrape → enrich → merge → generate → send.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ======================
# CONFIGURATION
# ======================
QUERY = "hair salons Minneapolis"
MAX_RESULTS = 30
CITY = "Minneapolis"
BATCH_SIZE = 20
# ======================

WORKSPACE = Path('/root/.openclaw/workspace')
SALON_LEADS_CSV = WORKSPACE / 'salon_leads.csv'
SALON_LEADS_ENRICHED = WORKSPACE / 'salon_leads_enriched.csv'
LEADS_MASTER_JSON = WORKSPACE / 'leads_master.json'
REMAINING_EMAILS_JSON = WORKSPACE / 'salon_emails_remaining.json'

# Scripts
SCRAPE_SCRIPT = WORKSPACE / 'pipelines' / 'scrape_new_leads.py'
ENRICH_SCRIPT = WORKSPACE / 'pipelines' / 'run_enrichment.sh'
REFRESH_MASTER_SCRIPT = WORKSPACE / 'pipelines' / 'refresh_master_from_enriched.py'
GENERATE_SCRIPT = WORKSPACE / 'pipelines' / 'generate_missing_emails.py'
SEND_SCRIPT = WORKSPACE / 'daily_website_batch.py'

def run(cmd, check=True, capture=False, **kwargs):
    print(f"$ {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    if capture:
        result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
        if check and result.returncode != 0:
            print(f"Error: {result.stderr}", file=sys.stderr)
            sys.exit(1)
        return result
    else:
        result = subprocess.run(cmd, **kwargs)
        if check and result.returncode != 0:
            sys.exit(1)
        return result

def step_scrape():
    print("\n=== Step 1: Scrape new leads from Google Maps ===")
    run([sys.executable, str(SCRAPE_SCRIPT), QUERY, str(MAX_RESULTS), CITY])

def step_enrich():
    print("\n=== Step 2: Enrich leads (extract emails, detect booking platforms) ===")
    # The shell script uses node; ensure it's executable
    run(['bash', str(ENRICH_SCRIPT)])

def step_refresh_master():
    print("\n=== Step 3: Refresh leads master ===")
    run([sys.executable, str(REFRESH_MASTER_SCRIPT)])

def step_generate():
    print("\n=== Step 4: Generate missing outreach emails ===")
    env = os.environ.copy()
    # Allow overriding via env if set
    run([sys.executable, str(GENERATE_SCRIPT)], env=env)

def step_send(dry_run=False, batch_size=None):
    print("\n=== Step 5: Send today's batch ===")
    cmd = [sys.executable, str(SEND_SCRIPT), '--batch-size', str(batch_size or BATCH_SIZE)]
    if dry_run:
        cmd.append('--dry-run')
    run(cmd)

def main():
    parser = argparse.ArgumentParser(description='Website Sales Daily Pipeline')
    parser.add_argument('--dry-run', action='store_true', help='Preview without sending')
    parser.add_argument('--batch-size', type=int, help='Override configured batch size')
    parser.add_argument('--skip-scrape', action='store_true', help='Skip fresh scrape; use existing leads')
    parser.add_argument('--skip-enrich', action='store_true', help='Skip enrichment (use existing enriched data)')
    parser.add_argument('--skip-send', action='store_true', help='Generate emails but do not send')
    args = parser.parse_args()

    print("=" * 50)
    print("Website Sales Pipeline Starting")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 1. Scrape (unless skipped)
    if not args.skip_scrape:
        step_scrape()
    else:
        print("\n=== Skipping scrape ===")

    # 2. Enrich (unless skipped)
    if not args.skip_enrich:
        step_enrich()
    else:
        print("\n=== Skipping enrichment ===")

    # 3. Refresh master
    step_refresh_master()

    # 4. Generate emails
    step_generate()

    # 5. Send (unless skip)
    if not args.skip_send:
        step_send(dry_run=args.dry_run, batch_size=args.batch_size)
    else:
        print("\n=== Skipping send ===")

    print("\n" + "=" * 50)
    print("Pipeline complete.")
    print("=" * 50)

if __name__ == '__main__':
    main()