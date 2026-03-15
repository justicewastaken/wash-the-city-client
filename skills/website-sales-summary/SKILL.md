---
name: website-sales-summary
description: "Daily summary report for website-sales pipeline: counts sent/failed emails, remaining pool, and lead statuses. Runs automatically at 11 PM CT."
---

# Website Sales Summary Skill

Provides daily metrics for your automated outreach pipeline.

## What It Does

Runs once per day (typically at 11 PM CT) and logs:
- Total emails sent today (across all batches)
- Total failures
- Remaining unsent emails in pool
- Lead status breakdown

Output appended to `daily_pipeline_summary.log` in your workspace.

## Usage

Usually runs automatically via cron. To run manually:

```bash
website-sales-summary
```

Or directly:
```bash
cd /root/.openclaw/workspace
python3 daily_pipeline_summary.py
```

## Configuration

The script looks for:
- `pipeline_send_*.log` files (created by send steps)
- `salon_emails_remaining.json`
- `leads_master.json`

All expected in workspace root.

## Scheduling

Cron job runs at 4 AM UTC (11 PM CT):
```
0 4 * * * /root/.openclaw/workspace/website-sales-summary >> /root/.openclaw/workspace/pipeline_summary.log 2>&1
```

Check log:
```bash
tail -f /root/.openclaw/workspace/pipeline_summary.log
```

---