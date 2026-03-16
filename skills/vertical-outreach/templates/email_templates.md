# Email Templates

These are the default templates used in the outreach sequence. They can be customized per vertical.

---

## Email 1: Initial Outreach

```
Subject: Quick question about {{vertical}} scheduling

Hey {{first_name}},

I was talking to a {{business_type}} owner who was spending 8–10 hours per week just calling patients to confirm appointments.

They were losing $2,800–$3,200 per month to no‑shows. Sound familiar?

I documented exactly how they solved it in this short case study:
{{case_study_url}}

It's a 5‑minute read that shows the exact SMS‑based system they implemented (no more phone tag).

If you're already using something similar, great — just ignore this.
But if you're still playing phone tag, it might be worth a look.

Either way, hope it helps.

—
J
```

---

## Email 2: Follow-up (3-4 days after Email 1)

```
Subject: Following up: {{vertical}} no‑show calculator

Hey {{first_name}},

Just circling back on the case study I sent.

I also built a quick calculator that shows exactly how much you're losing each month based on your numbers:
{{case_study_url}}

(It's embedded on the page — just fill in your appointments, average revenue, and no‑show rate.)

One {{business_type}} who used this system went from 22% no‑shows to 13% in 30 days. That's $2,400 back in their pocket every month.

If you want to implement something similar, reply to this email and I'll share how we could do it for your practice.

—
J
```

---

## Email 3: Final CTA (3-4 days after Email 2)

```
Subject: Last chance: {{vertical}} automation spots filling up

Hey {{first_name}},

I'm following up one last time about the no‑show automation system.

I've only got 3–4 spots open this month for full implementation ($1,500 setup, 3–5 days to go live). After that, I'm booking into next month.

If you're serious about cutting your no‑shows and recovering $2k–$3k per month, now's the time.

You can see the full case study here:
{{case_study_url}}

Or just reply "YES" and I'll get you on the calendar for a free 30‑minute consultation.

Either way, hope your practice is thriving.

—
J
```

---

## Personalization Variables

- `{{first_name}}` — Dentist's first name (from leads CSV)
- `{{vertical}}` — e.g., "dentist", "barber", "landscaper"
- `{{business_type}}` — e.g., "dental practice", "barbershop"
- `{{case_study_url}}` — URL of your Notion case study page
- `{{vertical.title()}}` — Capitalized vertical (template engine handles this)

---

## Customization Tips

- **Tone:** Keep it conversational, not salesy
- **Length:** 3–4 sentences max per email
- **Value:** Lead with the case study/results, not your service
- **CTA:** Clear next step (reply, book call, view calculator)
- **Frequency:** Space emails 3–4 days apart
- **Unsubscribe:** Include "Reply STOP to unsubscribe" if sending in volume
