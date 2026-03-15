---
name: website-sales-pipeline
description: "End-to-end daily automated outreach for local web design sales: scrape leads, enrich with emails/booking platforms, generate personalized emails, and send batches. Run daily to grow your pipeline."
---

# Website Sales Pipeline Skill

One-command daily automation for selling websites to local businesses.

## What It Does

Every time you run it:
1. Scrapes fresh Google Maps leads for your target query/city
2. Adds new leads to master list (deduped)
3. Enriches leads without emails via Playwright
4. Generates personalized outreach emails for new leads
5. Sends today's email batch (default 20)
6. Updates lead statuses and remaining pool

Perfect for: automated daily cold outreach to salons, restaurants, contractors, etc.

## Setup

### Prerequisites
- `gog` skill authenticated for Gmail sending
- Node.js + Playwright (for enrichment)
- Environment variables set:
  - `PORTFOLIO_URL` — your portfolio site
  - `YOUR_PHONE` — your phone number
  - (optional) `GOG_KEYRING_PASSWORD` if not already configured

### Configure
Edit the configuration at the top of `pipeline.py`:
- `QUERY` — Google Maps search (e.g., "hair salons Minneapolis")
- `MAX_RESULTS` — how many to scrape each run
- `CITY` — city name for email personalization
- `BATCH_SIZE` — how many emails to send each run

## Usage

Run the pipeline manually:
```bash
openclaw skills run website-sales-pipeline
```

Or call the CLI directly:
```bash
cd /root/.openclaw/workspace
./pipeline.py [--dry-run] [--batch-size N]
```

### Options
- `--dry-run` — preview without sending emails
- `--batch-size N` — override configured batch size
- `--skip-scrape` — only process existing leads (no fresh scrape)
- `--skip-send` — generate but don't send (for testing)

Examples:
```bash
# Test without sending
./pipeline.py --dry-run

# Scrape new leads but only generate emails (no send)
./pipeline.py --skip-send

# Send a larger batch
./pipeline.py --batch-size 30
```

## Scheduling (Cron)

Add to crontab to run daily e.g. 9 AM CT:
```bash
0 14 * * * /root/.openclaw/workspace/pipeline.py >> /root/.openclaw/workspace/pipeline.log 2>&1
```

(14:00 UTC = 9 AM CT)

## Files Managed

- `salon_leads.csv` — raw lead list (appended)
- `salon_leads_enriched.csv` — enriched with emails/booking platforms
- `leads_master.json` — master status tracker
- `salon_emails_remaining.json` — unsent email pool

All files stay in your workspace root.

## Customization

### Change Target Business Type
Modify `QUERY` in `pipeline.py`:
- "restaurants Minneapolis"
- "contractors Eau Claire"
- "nail salons Madison"

### Adjust Email Template
Edit the `TEMPLATE` string in `pipelines/generate_missing_emails.py` (still used by this skill). Supports placeholders:
- `{owner_name}`
- `{city}`
- `{business_name}`
- `{booking_platform}`
- `{YOUR_PHONE}`
- `{PORTFOLIO_URL}`

### Rate Limiting
The enrichment step visits websites with a 1.5s delay per lead. If you're scraping 50 new leads, that's ~75 seconds of enrichment time. The send step uses a 2.5s delay between emails by default.

## Monitoring

Check logs:
```bash
tail -f /root/.openclaw/workspace/pipeline.log
```

Check remaining emails:
```bash
python3 -c "import json; print(len(json.load(open('salon_emails_remaining.json'))))"
```

Check lead statuses:
```bash
python3 -c "import json; leads=json.load(open('leads_master.json')); from collections import Counter; print(Counter(l['status'] for l in leads))"
```

## Troubleshooting

**Scraper fails:** Playwright may need install: `node -e "require('playwright').install chromium()"` or run `npx playwright install chromium`

**Emails not sending:** Ensure `gog` is authenticated and `GOG_KEYRING_PASSWORD` is set in environment.

**No emails generated:** New leads may be missing `email` field after enrichment. Check `salon_leads_enriched.csv` for blank emails.

**Pipeline hangs:** Enrichment is slow; that's expected. Consider reducing `MAX_RESULTS` or running enrichment less frequently.

## Notes

- The skill uses your existing `website-sales` send functionality
- Duplicate detection prevents re-scraping same businesses
- Leads already marked `emailed`/`paid`/`closed-lost` won't get re-emailed
- City field must be provided in scrape step for proper personalization

---