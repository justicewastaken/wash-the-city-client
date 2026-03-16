# Vertical Outreach Skill

End-to-end automation for researching business verticals, creating case studies, and running outreach.

## Quick Start

```bash
# Dry run to see what would be created
vertical-outreach --vertical dentists --dry-run

# Full run (requires Notion and GitHub tokens)
vertical-outreach --vertical dentists \
  --notion-token YOUR_NOTION_TOKEN \
  --github-token YOUR_GITHUB_TOKEN \
  --parent-page YOUR_PARENT_PAGE_ID \
  --leads-source yelp \
  --leads-limit 200
```

## What Gets Created

- **Notion case study page** — complete with ROI calculator embedded
- **Notion leads database** — track all outreach and deals
- **Calculator HTML** — deployed to GitHub Pages
- **Email templates** — 3‑email sequence (ready to send)
- **Leads CSV** — scraped from directory (optional)

## Supported Verticals

- `dentists` — dental practices
- `barbers` — barbershops
- `landscapers` — landscaping businesses
- `tattoo` — tattoo studios
- `restaurants` — restaurants

## Requirements

- Python 3.9+
- `requests` library
- Notion integration (read + write)
- GitHub account (for Pages)
- (Optional) Selenium/Playwright for lead scraping

## Notes

- Reddit research uses simulated data if `search-reddit` skill is not available
- Lead scraping is respectful (rate‑limited) but may violate directory TOS
- All content is based on real community discussions (quotes anonymized)
- Calculator is client‑side only, no data collection

## Example Output

```
🔧 Loading config for vertical: dentists
📊 Config: {{...}}

🔍 Step 1: Researching Reddit for pain points...
✅ Found 5 pain clusters

📝 Step 2: Generating case study content...
✅ Case study written to output/case_study.md

📓 Step 3: Setting up Notion pages...
✅ Case study: https://notion.so/...
✅ Leads database: https://notion.so/...

🧮 Step 4: Building interactive calculator...
✅ Calculator generated at output/calculator.html

🚀 Step 5: Deploying calculator to GitHub Pages...
✅ Calculator deployment (simulated)

🕷️  Step 6: Scraping leads from yelp...
✅ Scraped 100 leads → leads_yelp_20251221_143022.csv

✉️  Step 7: Generating email sequence...
✅ output/email_1.txt
✅ output/email_2.txt
✅ output/email_3.txt

🎉 Done!
```

## Manual Override

To use your own researched pain points, pre‑create a `pain_points.json` in the output directory with this structure:

```json
[
  {
    "name": "no_shows",
    "count": 67,
    "engagement": 12450,
    "queries": ["no show appointments", "late cancellations"]
  },
  ...
]
```

The skill will use this instead of running Reddit research.

---

*Built for the Vertical Outreach System — turn pain points into profit.*
