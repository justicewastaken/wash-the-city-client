---
name: website-sales
description: "End-to-end website sales workflow for local businesses: lead finding, personalized outreach, Whop payment integration, and follow-up automation. Use when selling websites to solo/small businesses and needing to automate the sales pipeline."
---

# Website Sales Skill

Streamline your website sales process targeting local solo/small businesses. This skill automates lead generation, personalized outreach, payment collection via Whop, and follow-up tracking.

## When to Use

✅ **USE this skill when:**

- "Find local businesses that need websites"
- "Help me sell websites to small businesses"
- "Create an outreach campaign for web design services"
- "Set up Whop payments for website setup fees"
- "Automate follow-ups for website leads"
- "Generate personalized emails for businesses without websites"
- "Track my website sales pipeline"

❌ **DON'T use this skill when:**

- Building actual websites (use coding-agent or Claude directly)
- General web development tasks
- Non-local or enterprise sales strategies
- Non-Whop payment processing

## Quick Start

### 1. Find Leads
```bash
website-sales find-leads --city "Eau Claire" --count 50 --output leads.json
```

### 2. Draft Outreach
```bash
website-sales draft-outreach --leads leads.json --template initial --output emails.json
```

### 3. Send & Track
```bash
website-sales send-emails --emails emails.json --dry-run  # review first
website-sales send-emails --emails emails.json           # actually send
```

### 4. Payment Links
```bash
website-sales generate-payment --lead "Business Name" --email "owner@example.com" --type "setup+monthly"
```

### 5. Follow-ups
```bash
website-sales schedule-followups --leads leads.json --days 3,7,14
```

## Commands Reference

### `find-leads`
Scrape local business directories to find solo/small businesses with outdated or missing websites.

**Options:**
- `--city`: Target city (e.g., "Eau Claire", "Minneapolis")
- `--count`: Number of leads to find (default: 50)
- `--radius`: Search radius in miles (default: 25)
- `--output`: Output file (JSON, default: leads.json)
- `--industries`: Comma-separated industries (default: all)

**Example:**
```bash
website-sales find-leads --city "Eau Claire" --count 30 --industries restaurant,salon,contractor
```

### `draft-outreach`
Generate personalized email drafts for each lead based on their business type and current website.

**Options:**
- `--leads`: Input leads JSON file
- `--template`: Template type (initial, followup-3d, followup-7d)
- `--output`: Output file (JSON with emails)
- `--whop-product`: Whop product ID to include in payment links

**Example:**
```bash
website-sales draft-outreach --leads leads.json --template initial --output emails.json
```

### `send-emails`
Send drafted emails via Gmail and update lead status.

**Options:**
- `--emails`: Input emails JSON file
- `--dry-run`: Preview without sending
- `--batch-size`: How many to send at once (default: 25)
- `--gmail-account`: Which Gmail account to use (default: primary)

**Example:**
```bash
website-sales send-emails --emails emails.json --dry-run
website-sales send-emails --emails emails.json --batch-size 20
```

### `generate-payment`
Create a unique Whop payment link for a lead.

**Options:**
- `--lead`: Business name
- `--email`: Customer email
- `--type`: Package type (setup-only, monthly, setup+monthly)
- `--whop-api-key`: Whop API key (or set WHOP_API_KEY env var)

**Example:**
```bash
website-sales generate-payment --lead "Main Street Cafe" --email "owner@example.com" --type "setup+monthly"
```

### `track-leads`
Update lead status and add notes.

**Options:**
- `--lead-id`: Lead identifier
- `--status`: New status (contacted, responded, sent-payment, paid, closed-lost)
- `--notes`: Optional notes
- `--leads-file`: Leads JSON to update

**Example:**
```bash
website-sales track-leads --lead-id "main-street-cafe" --status "responded" --notes "Requested call Tuesday"
```

### `schedule-followups`
Add follow-up reminders to Google Calendar.

**Options:**
- `--leads`: Input leads JSON
- `--days`: Days after initial email (comma-separated)
- `--calendar`: Calendar ID (default: primary)

**Example:**
```bash
website-sales schedule-followups --leads leads.json --days 3,7,14
```

## Templates

The skill includes email templates:
- **initial**: Introduction with portfolio link, Whop offer
- **followup-3d**: Gentle reminder after 3 days
- **followup-7d**: Second follow-up with social proof
- **followup-14d**: Final "closing" email

Customize templates in `references/email-templates.md`.

## Whop Integration

1. Create a Whop product with two variants:
   - "Website Setup Only" ($X one-time)
   - "Website Setup + Monthly Maintenance" ($X setup + $100/mo)

2. Get your Whop API key from Dashboard → Settings → API

3. Set environment variable:
   ```bash
   export WHOP_API_KEY="your_key_here"
   ```

4. Or pass `--whop-api-key` to commands

The skill generates unique payment links and can automatically mark leads as "paid" when Whop confirms.

## Configuration

Before first use, set:

```bash
export GOG_KEYRING_PASSWORD="your_gog_password"  # for Gmail/Calendar
export WHOP_API_KEY="your_whop_key"
```

Your Gmail credentials should already be configured via the gog skill.

## Output Files

- `leads.json`: Lead list with name, email, website, source, status
- `emails.json`: Draft emails ready to review/send
- `pipeline.csv`: Google Sheet-compatible tracking export

## Workflow Overview

```
1. find-leads → leads.json
2. draft-outreach → emails.json
3. review emails (human) → approve
4. send-emails → updates leads with sent status
5. track responses → update lead status
6. generate-payment → creates Whop link
7. schedule-followups → calendar reminders
```

## Tips

- Start with 50 leads to test the workflow
- Personalize at least 2 details per email (business name, industry-specific hook)
- Send in batches of 25-50 to avoid Gmail rate limits
- Monitor responses and tweak templates based on reply rates
- Always include your portfolio link in initial outreach

## Troubleshooting

**No leads found:** Try a larger city or increase count. Some smaller towns may have limited targets.

**Emails bouncing:** Verify lead emails with additional tools; consider using hunter.io or similar (not included).

**Whop links not working:** Ensure API key is set and product is active in Whop dashboard.

**Gmail not sending:** Check gog skill is authenticated. New Gmail accounts have daily limits (~50-100/day for warm accounts).

---

Need help? Check `references/` for detailed guides on each command.
