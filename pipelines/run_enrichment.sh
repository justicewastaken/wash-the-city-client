#!/bin/bash
# Run enrichment script (processes salon_leads.csv -> salon_leads_enriched.csv)
cd /root/.openclaw/workspace
node skills/playwright-scraper/scripts/enrich_salons_v2.js