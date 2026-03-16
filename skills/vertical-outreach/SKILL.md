# Vertical Outreach Automation

End-to-end system for identifying business pain points, creating case studies, generating leads, and running outreach campaigns.

## What It Does

1. **Research** a vertical (e.g., dentists, barbers, landscapers) using Reddit to find the most urgent, high-engagement pain points
2. **Build** a complete case study page in Notion with technical implementation details, ROI calculator, and objection handling
3. **Create** a Notion database for tracking leads and outreach
4. **Deploy** an interactive revenue calculator to GitHub Pages
5. **Scrape** leads from directories (optional)
6. **Generate** email sequences personalized for the vertical
7. **Export** everything ready for manual or automated sending

## Usage

```bash
vertical-outreach --vertical dentists --notion-token YOUR_TOKEN --github-token YOUR_GITHUB_TOKEN
```

## Options

- `--vertical VERTICAL` - Target business type (e.g., dentists, barbers, landscapers)
- `--subreddit SUBREDDIT` - Specific subreddit to research (defaults based on vertical)
- `--days DAYS` - Days back to research (default: 180)
- `--notion-token TOKEN` - Notion integration token
- `--github-token TOKEN` - GitHub token for Pages deployment
- `--parent-page PAGE_ID` - Notion parent page ID (optional)
- `--leads-source SOURCE` - Scrape leads: `yelp`, `healthgrades`, `zocdoc`, `none` (default: none)
- `--leads-limit N` - Max leads to scrape (default: 100)
- `--dry-run` - Test without creating Notion pages or deploying
- `--output-dir DIR` - Where to save generated files (default: ./output)

## Output

- Notion case study page URL
- Notion leads database URL
- Calculator page URL (GitHub Pages)
- Email templates (3-email sequence)
- Optional: CSV of scraped leads

## Example

```bash
# Full run for dentists
vertical-outreach --vertical dentists --notion-token ntn_xxx --github-token ghp_xxx --leads-source yelp --leads-limit 200

# Dry run to see what would be created
vertical-outreach --vertical barbers --notion-token ntn_xxx --dry-run
```

## Requirements

- Python 3.9+
- `requests` library
- Notion integration token (with read/write access)
- GitHub personal access token (repo + pages permissions)
- (Optional) Selenium/Playwright for lead scraping

## Vertical Configs

Built-in configs for:
- `dentists` → subreddits: dentistry, dentistas
- `barbers` → subreddits: barbers, barbershop
- `landscapers` → subreddits: landscaping, landscapers
- `tattoo` → subreddits: tattoo, tattooing
- `restaurants` → subreddits: restaurant, smallbusiness

Custom verticals can be added via `--subreddit` flag.

## Workflow

1. **Research** → Reddit API → cluster pain points → rank by engagement
2. **Content** → Generate case study with real quotes, ROI math, objection handling
3. **Notion** → Create case study page + leads database under parent
4. **Calculator** → Build interactive HTML → deploy to GitHub Pages → embed in case study
5. **Leads** → Scrape directories → clean/format → export CSV + add to Notion DB
6. **Emails** → Write 3-email sequence referencing case study & calculator

All artifacts saved to `./output/` for reference.

## Notes

- Respectful scraping: rate limits, delays, robots.txt
- All content based on real Reddit discussions (quotes anonymized)
- Calculator uses client-side only (no data collection)
- Leads scraping may violate directory TOS — use responsibly
