#!/bin/bash
set -e

cd /root/.openclaw/workspace

# Configuration: adjust these as needed (or pass as args)
QUERY="hair salons Minneapolis"
MAX_RESULTS=30
CITY="Minneapolis"

echo "=== Starting full daily pipeline ==="

# Step 1: Scrape new leads from Google Maps
echo "[1/5] Scraping new leads..."
python3 pipelines/scrape_new_leads.py "$QUERY" "$MAX_RESULTS" "$CITY"

# Step 2: Enrich leads (get emails, booking platform)
echo "[2/5] Enriching leads..."
pipelines/run_enrichment.sh

# Step 3: Merge new enriched leads into master
echo "[3/5] Refreshing leads master..."
python3 pipelines/refresh_master_from_enriched.py

# Step 4: Generate missing emails for new leads
echo "[4/5] Generating outreach emails..."
python3 pipelines/generate_missing_emails.py

# Step 5: Send today's batch (default 20, change as needed)
echo "[5/5] Sending today's batch..."
python3 daily_website_batch.py --send --batch-size 20

echo "=== Full pipeline complete ==="