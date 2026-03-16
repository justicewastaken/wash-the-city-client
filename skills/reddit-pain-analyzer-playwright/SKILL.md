# Reddit Pain Analyzer (Playwright Stealth)

Scrapes Reddit with anti-bot protection using Playwright Stealth. No API key needed. Bypasses Cloudflare and Reddit's bot detection.

## Usage

```bash
node reddit-pain-analyzer-playwright.js <subreddit> [days_back=180] [min_comments=3]
```

## Examples

```bash
# Analyze r/dentistry pain points from last 6 months
node reddit-pain-analyzer-playwright.js dentistry 180 5

# Quick test: last 7 days, minimum 2 comments
node reddit-pain-analyzer-playwright.js dentistry 7 2
```

## Requirements

- Node.js 18+
- `playwright` package
- Chromium browser (auto-installed by Playwright)

## Installation

```bash
npm init -y
npm install playwright
# Playwright will auto-download chromium on first run
```

## How It Works

1. Launches Chromium with stealth settings (hides automation)
2. Uses iPhone user agent and realistic viewport
3. Navigates directly to Reddit's JSON API endpoint (`/search.json`)
4. Extracts posts with engagement metrics (score, upvote_ratio, comments)
5. Analyzes text for pain keywords
6. Ranks pain clusters by total engagement (upvotes + weighted comments)
7. Outputs JSON file and human-readable summary

## Output

- `{subreddit}_pain-analysis_YYYY-MM-DD_HH-MM-SS.json` — full data
- Terminal summary with top pain clusters ranked by engagement

## Why This Works When Others Fail

- **Stealth mode:** Hides `navigator.webdriver`, uses real device UA
- **Direct JSON endpoint:** Doesn't rely on HTML scraping
- **Realistic delays:** Waits for content to load naturally
- **No API key:** Completely free, no rate limits from OpenAI

## Sample Output

```
🕷️  Scraping r/dentistry via Playwright Stealth...
📡 Navigating to: https://www.reddit.com/r/dentistry/search.json?q=&restrict_sr=on&sort=new&limit=100&t=all
📡 HTTP Status: 200
📦 Found 100 posts in JSON response
✅ Collected 87 posts from r/dentistry

📊 Analyzing posts for pain points...

==============================================================
PAIN CLUSTER REPORT: r/dentistry
==============================================================
Total posts analyzed: 87
Posts with detected pain points: 72

Top Pain Clusters (ranked by total engagement):
----------------------------------------------------------------------

APPOINTMENTS: 34 posts (total engagement: 12,450)
  • "No-shows are killing my practice..." (score: 234, comments: 142)
    https://reddit.com/r/dentistry/comments/...
  • "Patients constantly cancel last minute..." (score: 189, comments: 89)
    https://reddit.com/r/dentistry/comments/...
```

## Troubleshooting

If you get 403:
- Increase wait time: `WAIT_TIME=15000 node reddit-pain-analyzer-playwright.js dentistry 180 5`
- Try headful mode: `HEADLESS=false node ...`
- The script will save `debug_{subreddit}.html` on failure for inspection
