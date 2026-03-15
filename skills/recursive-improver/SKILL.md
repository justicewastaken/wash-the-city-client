---
name: recursive-improver
description: "Twice-daily self-improvement for website-sales pipeline: analyzes email performance, adjusts templates/batching, and logs changes. Runs automatically to optimize outreach over time."
---

# Recursive Improver Skill

Continuous optimization for automated outreach. Runs 2x/day and makes small, safe adjustments based on recent performance.

## What It Does

Each run:

1. **Metrics collection** — reads send logs, leads status, reply detection
2. **Analysis** — calculates reply rates, identifies patterns (city, booking platform, email domain)
3. **Adjustment** — proposes and optionally applies changes:
   - Toggle between email template variants
   - Increase/decrease batch sizes (within limits)
   - Reorder unsent leads by predicted reply rate
   - Adjust send time offsets (if multiple batches)
4. **Logging** — records all decisions and rationale in `.learnings/IMPROVEMENTS.md`
5. **Preview** — by default, only reports planned changes; use `--auto-apply` to execute

## Configuration

Edit `improver_config.json` in workspace root:
```json
{
  "schedule": "0,12 * * *",   // cron pattern (default: twice daily at midnight/noon UTC)
  "auto_apply": false,       // default to dry-run; set true to auto-commit changes
  "max_batch_size": 30,      // never exceed this per batch
  "min_batch_size": 5,
  "template_variants": ["v1", "v2"], // to A/B test different email bodies
  "metrics_window_days": 3   // how far back to analyze performance
}
```

## Usage

Run manually:
```bash
recursive-improver [--auto-apply] [--dry-run]
```

Options:
- `--auto-apply` — actually modify files (emails, config)
- `--dry-run` — preview only (default)

## How It Works

- Reads send logs from `pipeline_send_*.log`
- Reads lead statuses from `leads_master.json`
- Identifies replies via `notify_replies.py` output or Gmail labels (future)
- Adjusts the unsent email pool (`salon_emails_remaining.json`)
- Suggests template/style changes based on A/B test results

## Safety

- Changes are incremental and reversible
- All actions logged with before/after diffs
- You can always revert using version control (git) or backups
- By default, `--auto-apply` is off; review `.learnings/IMPROVEMENTS.md` first

## Monitoring

Check the log:
```bash
tail -f /root/.openclaw/workspace/pipeline_summary.log
```

Review proposed changes:
```bash
cat /root/.openclaw/workspace/.learnings/IMPROVEMENTS.md
```

## Schedule

Cron added automatically (if not present):
```
0 6,18 * * * /root/.local/bin/recursive-improver >> /root/.openclaw/workspace/improver.log 2>&1
```
(Runs 6 AM and 6 PM CT daily)

---