---
name: email-ab-testing
description: "Add A/B testing to website-sales outreach: multiple email variants, split testing, performance tracking, and automatic optimization via recursive-improver."
---

# Email A/B Testing Skill

Enhances `website-sales-pipeline` with variant testing and automatic winner selection.

## What It Does

- Defines multiple email template variants (A, B, C…) in `email_variants.json`
- During generation, assigns each new lead a variant based on config (round-robin or weighted)
- Tracks which variant was sent to each lead in `leads_master.json`
- Recursive improver computes reply rates per variant and suggests reweighting
- Optionally auto-promotes the winning variant to 100% after statistical significance

## Setup

1. Create `email_variants.json` in workspace root. Example:

```json
{
  "variants": [
    {
      "id": "v1",
      "subject": "UW-Eau Claire student building salon websites",
      "body": "Hey {owner_name},\n\nI'm a UW-Eau Claire student...\n\nBest,\nJustice"
    },
    {
      "id": "v2",
      "subject": "Custom website for {business_name} at a student rate",
      "body": "Hi {owner_name},\n\nI came across {business_name}...\n\nThanks,\nJustice"
    }
  ],
  "default_variant": "v1",
  "distribution": "uniform"  // uniform or weights object
}
```

2. Enable in `improver_config.json`: `"ab_testing": true`

## Usage

- Generation script `generate_missing_emails.py` automatically picks variants for new leads.
- Existing unsent emails keep their assigned variant.
- The `recursive-improver` analyzes reply rates by variant and updates distribution in `improver_config.json`.
- Set `"auto_promote": true` to automatically set distribution to 100% for the top variant after 30+ emails and >95% confidence.

## Metrics

Review in `email_ab_report.json` (generated daily). Includes:
- Emails sent per variant
- Reply count / reply rate
- Statistical comparison (p-value if simple binomial test)
- Current distribution

## Notes

- Variants use placeholders: `{owner_name}`, `{business_name}`, `{city}`, `{booking_platform}`
- Keep variants similar in length and tone; only tweak subject, first paragraph, CTA.
- Do not change the overall value proposition; test incremental improvements.

---