# Reddit Pain Analyzer

Find recurring business problems in any subreddit. Scrapes Reddit directly, clusters pain points by engagement (upvotes + comments), identifies automation opportunities.

## Usage

```bash
reddit-pain-analyzer <subreddit> [days_back=180] [min_comments=3]
```

## Examples

```bash
# Analyze r/dentistry pain points from last 6 months
reddit-pain-analyzer dentistry 180 5

# Analyze r/barbershop from last 90 days
reddit-pain-analyzer barbershop 90 3
```

## Output

- JSON file with pain clusters ranked by total engagement
- Terminal summary showing top pain clusters with example quotes
- Includes upvote scores, comment counts, upvote ratios

## What it does

1. Scrapes posts from the specified subreddit (last N days, minimum comment threshold)
2. Fetches full post data including engagement metrics (score, upvote_ratio)
3. Analyzes titles and text for pain-related keywords
4. Clusters posts by pain category
5. Ranks clusters by total engagement (upvotes + comments weighted)
6. Outputs JSON with examples and a human-readable summary

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

## Installation

Copy this skill folder to your OpenClaw workspace or install via Clawhub (if published).

## Sample Output

```
PAIN CLUSTER REPORT: r/dentistry
============================================================
Total posts analyzed: 247
Posts with detected pain points: 189

Top Pain Clusters (by engagement):
------------------------------------------------------------

APPOINTMENTS: 67 posts (total engagement: 12,450)
  • "No-shows are killing my practice..." (score: 234, 142 comments)
    https://reddit.com/r/dentistry/comments/...
  • "Patients constantly cancel last minute..." (score: 189, 89 comments)
    https://reddit.com/r/dentistry/comments/...

INSURANCE: 52 posts (total engagement: 9,230)
  • "Insurance verification takes hours..." (score: 456, 234 comments)
    https://reddit.com/r/dentistry/comments/...
...
```
