# Website Sales Skill - Setup Guide

Complete setup before first use. Expect ~30-45 minutes.

## Prerequisites

1. **OpenClaw workspace** - Skill lives in `skills/website-sales/`
2. **gog skill configured** - Gmail and Calendar access working
3. **Whop account** - Create product(s) for website offers
4. **Whop API key** - From Dashboard → Settings → API
5. **Portfolio website** - Have 2-3 sample sites ready

## Step 1: Install Dependencies (One-time)

```bash
# Install googlesearch-python for lead finding
pip install googlesearch-python

# Install requests (if not already) for Whop API fallback
pip install requests
```

The skill will use gog CLI (already installed via gog skill) for email/calendar.

## Step 2: Configure Whop

1. Log into Whop dashboard
2. Create a product:
   - Name: "Website Setup + Maintenance"
   - Variants:
     - Website Setup Only: $X (one-time)
     - Monthly Maintenance: $100/mo
     - Setup + Monthly: $X + first month
   - Configure checkout settings (tax, refunds, etc.)
3. Copy your **Product ID** from the URL: `https://whop.com/dashboard/products/[PRODUCT_ID]`
4. Copy your **API Key** from Dashboard → Settings → API
5. Save config:
   ```bash
   cp skills/website-sales/references/whop-config-template.json skills/website-sales/references/whop-config.json
   # Edit whop-config.json with your product ID and prices
   export WHOP_API_KEY="your_api_key_here"  # Or use --whop-api-key flag
   ```

## Step 3: Prepare Your Portfolio

Have these URLs ready:
- Main portfolio site (or GitHub Pages)
- 2-3 sample websites (preferably in similar industries you'll target)
- Loom video template (optional but helpful)

Store portfolio URL in environment for convenience:
```bash
export PORTFOLIO_URL="https://yourportfolio.com"
export YOUR_PHONE="555-555-5555"
```

## Step 4: Test the Pipeline

Run these commands in order:

```bash
# 1. Find 10 test leads (Eau Claire)
website-sales find-leads --city "Eau Claire" --count 10 --output test-leads.json

# 2. Check leads file - you'll need to have emails populated
cat test-leads.json | jq '.[0:3]'  # inspect first 3

# If leads don't have emails, you'll need to enrich manually or with additional tools.
# For now, add email addresses to the leads.json file manually or with a script.
```

**Enriching emails:**

The `find-leads` script can be extended to find owner emails. Quick manual method:
1. Open a few business websites
2. Look for contact pages or "About Us" with owner info
3. Common email formats: `info@`, `hello@`, `contact@`, or `firstlast@`
4. Update the leads JSON:

```json
{
  "name": "Main Street Cafe",
  "city": "Eau Claire",
  "email": "owner@mainstreetcafe.com",
  "website": "https://mainstreetcafe.com",
  "status": "prospect"
}
```

```bash
# 3. Draft outreach emails
website-sales draft-outreach --leads test-leads.json --portfolio-url $PORTFOLIO_URL --your-phone $YOUR_PHONE --output test-emails.json

# 4. Preview first email
head -n 20 test-emails.json | jq '.[0]'

# 5. Dry-run send (no actual emails)
website-sales send-emails --emails test-emails.json --leads test-leads.json --dry-run

# 6. Send first batch (if everything looks good)
website-sales send-emails --emails test-emails.json --leads test-leads.json --batch-size 5
```

## Step 5: Generate Payment Links

When a lead responds positively:

```bash
website-sales generate-payment \
  --lead "Main Street Cafe" \
  --email "owner@example.com" \
  --type "setup+monthly" \
  --output payments.json
```

Copy the generated link and send via email (or include in your Loom video).

## Step 6: Follow-up Automation

Schedule reminders for all emailed leads:

```bash
website-sales schedule-followups --leads test-leads.json --days 3,7,14 --dry-run
website-sales schedule-followups --leads test-leads.json --days 3,7,14
```

This creates calendar events for follow-ups.

## Step 7: Track Progress

The skill updates:
- `leads.json` - all leads and their status
- `emails.json` - drafted emails
- `payments.jsonl` - payment links created (one JSON per line)

Export to CSV/Google Sheets for analysis:

```bash
python -c "import json, csv; data=json.load(open('leads.json')); csv.DictWriter(open('leads.csv','w'), fieldnames=data[0].keys()).writerows(data)"
```

## All-in-One Workflow Script

For daily use, you can chain commands:

```bash
#!/bin/bash
# daily_outreach.sh
set -e

CITY="${1:-Eau Claire}"
COUNT="${2:-50}"

echo "=== Website Sales Outreach for $CITY ==="
echo "[1/5] Finding leads..."
website-sales find-leads --city "$CITY" --count $COUNT --output leads.json

echo "[2/5] Enriching emails (manual step recommended)"
# TODO: integrate email finder

echo "[3/5] Drafting emails..."
website-sales draft-outreach --leads leads.json --portfolio-url $PORTFOLIO_URL --your-phone $YOUR_PHONE --output emails.json

echo "[4/5] Send emails (review first!)"
website-sales send-emails --emails emails.json --leads leads.json --dry-run
read -p "Proceed with sending? (y/N): " confirm
if [[ $confirm == [yY] ]]; then
    website-sales send-emails --emails emails.json --leads leads.json --batch-size 25
fi

echo "[5/5] Scheduling follow-ups..."
website-sales schedule-followups --leads leads.json --days 3,7,14

echo "Done! Check leads.json for status updates."
```

Make it executable: `chmod +x daily_outreach.sh`

---

## Troubleshooting

**"gog: command not found"** → Ensure gog skill installed and authenticated.

**"No leads with email addresses"** → The find-leads script is a starting point; you'll need to manually add business owner emails or integrate a service like hunter.io.

**"Gmail rate limit exceeded"** → New Gmail accounts can only send ~50 emails/day. Use an established account or spread outreach over multiple days.

**"Whop API error"** → Verify API key, product ID, and that the product is active in Whop dashboard.

**Placeholder emails not replaced** → Check that leads.json has `email` field populated. The draft-outreach script only processes leads with email addresses.

---

## Next Steps

Once setup is complete:
1. Run your first real outreach batch (start with 20-30)
2. Monitor responses (check Gmail)
3. Respond promptly with Loom video + Whop link
4. Update lead status as they move through pipeline
5. Adjust templates based on reply rates

Happy selling! 🚀
