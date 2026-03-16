# Reddit Pain Scraper

Scrapes Reddit subreddits to identify recurring business pain points. Perfect for finding automation opportunities and validating product ideas.

## Usage

```bash
reddit-pain-scraper <subreddit> [days_back=180] [min_comments=3]
```

## Examples

```bash
# Scrape r/dentistry for pain points from last 6 months
reddit-pain-scraper dentistry 180 5

# Scrape r/barbershop for last 90 days
reddit-pain-scraper barbershop 90 3
```

## Output

- JSON file with clustered pain points and example posts
- Terminal summary showing top pain clusters
- All data saved locally for analysis

## What it does

1. Fetches posts from the specified subreddit (last N days, minimum comment threshold)
2. Analyzes titles and text for pain-related keywords (time loss, frustration, manual work, etc.)
3. Clusters posts by pain category
4. Outputs JSON with examples and a human-readable summary

## Pain Categories Detected

- time_management
- money_loss
- frustration
- scattered
- follow_up
- paperwork
- appointments
- insurance
- communication

## Use Cases

- Validate automation ideas before building
- Identify high-demand services for local businesses
- Create targeted content (guides, cold email campaigns)
- Find niches for SaaS products

## Requirements

- Python 3
- `requests` library (`pip install requests`)
