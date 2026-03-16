# Case Study: How We Cut No Shows by 40% for a Dental Practice

*Real results from a recent implementation in a Wisconsin dental practice*

---

## The Challenge

Our client, a 3-chair dental practice, was losing $2,800–$3,200 per month to no shows.

Their no shows rate was ~22% — nearly 1 in 4 appointments.

They tried phone call reminders. It didn't work:

- Front desk staff spending 8–10 hours per week on reminder calls
- Patients ignoring calls or screening them
- No way to track who actually received the reminder
- No rescheduling functionality — patients just said "I'll call back" (and rarely did)

---

## Our Solution: Two-Way SMS Automation

We built an automated system that sends timed reminders with one-click confirm/reschedule buttons.

### How It Works

```
48 hours before → reminder with CONFIRM/RESCHEDULE
24 hours before → reminder (if not confirmed)
2 hours before → final reminder (if not confirmed)
```

Patients reply:
- **"CONFIRM"** → status automatically updated to confirmed
- **"RESCHEDULE"** → tagged for staff follow-up with suggested times
- **No reply** → flagged for manual outreach 15 minutes after appointment time

The system also automatically:
- Sends a notification 15 minutes past scheduled time
- Tags patients who no-show for follow-up campaigns
- Optionally charges a cancellation fee if card on file

---

## Technical Implementation

**Platform:** GoHighLevel

**Custom Fields Added:**
- `appointment_status` (scheduled, confirmed, no-show, cancelled)
- `last_reminder_sent` (timestamp)
- `reminder_sequence` (1, 2, 3)
- `sms_response` (captures patient replies)

**SMS Template (optimized for response):**

> "Hi {first_name}, this is {practice_name} confirming your appointment on {date} at {time}. Reply CONFIRM to confirm or RESCHEDULE to change. Standard message rates apply."

**Monthly Costs:**
- GoHighLevel: $29/mo
- SMS credits: ~$0.02/message × ~3 messages per appointment = ~$60–80/mo for 100 appointments/day

---

## Results After 30 Days

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| no-show rate | 22% | 13% | ↓ 40% |
| revenue recovered | — | $2,400 | +$2,400 |
| front desk time | 8–10 hrs/wk | 1–2 hrs/wk | ↓ 80% |
| sms cost | $0 | ~$50 | — |
| net monthly gain | — | ~$2,350 | ROI: 19% |

Patient feedback: Positive — patients appreciated the convenience of text reminders. No complaints about frequency or content.

---

## Why This Works (vs. Phone Calls)

- **Asynchronous** — Patients respond when convenient, not during business hours
- **Trackable** — Every reminder is logged; you know who saw it, who confirmed
- **Two-way** — Patients can reschedule with one reply, reducing friction
- **Automated** — Zero front desk time after setup
- **Scalable** — Works the same for 100 or 1,000 patients

---

## 💰 How Much Are You Missing Out On?

Use our interactive calculator to see your exact revenue loss:

➡️ [Open the Calculator](https://justicewastaken.github.io/-dental-noshow-calculator/calculator.html)

*(Calculator embedded below)*

---

## The Beliefs That Keep Dental Practice Owners Stuck (And Why They're Wrong)

### ❌ "I don't have the budget for this right now."

The truth: You can't afford NOT to.
If you're losing $2,400/month to no shows (22% rate on $10k revenue), that's $28,800 per year disappearing.
Our solution costs $1,500 one-time or $500/mo. Even at the highest end, you break even in less than one month of recovered revenue.
This isn't an expense — it's a revenue recovery system.

### ❌ "We already try to remind patients. It doesn't work."

The truth: You're using the wrong tool.
Phone calls have a 10% response rate at best. SMS has a 98% open rate and 45% response rate.
The difference isn't effort — it's medium. When you switch from calls to two-way SMS, the results are immediate and dramatic.

### ❌ "My patients don't like getting texts from us."

The truth: They prefer it.
In our implementation, we received zero complaints. Why? Because texts are asynchronous — patients respond on their schedule.
The messages are simple, clear, and give them control (CONFIRM or RESCHEDULE).

### ❌ "We already have a reminder system."

The truth: Is it two-way? Does it capture responses automatically?
Most "reminder systems" are one-way blasts: "Don't forget your appointment!" with no way to reply.
That's not a solution — that's broadcasting.
The magic is in the response capture: when a patient texts "RESCHEDULE," the system automatically tags them and notifies staff with suggested times.

### ❌ "I don't want to switch to a new CRM. Our current system is fine."

The truth: Your current system isn't preventing $2,400/month losses.
We can migrate your data in a few hours. The ROI is so fast, you'll be glad you switched within 30 days.

The question isn't "Do I want to change CRMs?" It's "Do I want to recover $2,400/month?"

### ❌ "I'll just have my staff call patients. It's cheaper."

The truth: It's already costing you more than you realize.
Your front desk spends 8–10 hours per week on reminder calls. That's $200–$300 in labor for a solution that doesn't work.
SMS costs ~$60–80/month and actually gets responses.
You save ~$200/month in labor *plus* recover $2,400 in revenue.
Doing it yourself isn't cheaper — it's more expensive because it's ineffective.

### ❌ "This sounds too good to be true."

The truth: It's not. It's proven.
We're showing you a real case study with real numbers from a real dental practice.
The technology is standard and reliable. The workflow is straightforward.
The only reason it seems too good to be true is because you've been tolerating the problem for so long that $2,400/month in losses feels "normal."
It's not normal. It's fixable.

### ❌ "I need to think about it."

The truth: Thinking won't change the math.
Every day you wait, you're losing $80–$100.
In 30 days, that's another $2,400 gone.
The decision should be easy: spend $1,500 to stop losing $2,400/month.

We get it — change is uncomfortable. But the cost of staying the same is $28,800 per year.

---

## Investment

We offer two options:

### Option 1: Full Implementation (Done-For-You)
**One-time setup: $1,500**

Includes:
- Complete GoHighLevel workflow configuration
- Custom SMS templates (optimized for your practice tone)
- Integration with your existing appointment calendar
- Testing with 10–20 appointments to ensure flawless operation
- 30 days of support (tweaks, adjustments, troubleshooting)
- Documentation and 1-hour staff training session

**Timeline:** 3–5 days from start to live

### Option 2: Ongoing Management
**Monthly fee: $500/mo**

Includes:
- Full system monitoring
- Monthly optimization based on performance data
- SMS template tweaks and A/B testing
- Report on no-show metrics and revenue recovered
- Priority support

First-time clients often start with Option 1 and add Option 2 after seeing the results.

---

## Next Steps

If you're ready to eliminate no shows and recover $2k–$3k per month:

1. **Book a free 30-minute consultation** to discuss your current setup and get a precise timeline
   - [Click here to schedule](https://calendly.com/your-link) *(insert your Calendly)*

2. **Or reply to this email** with:
   - Your current no shows rate (if known)
   - Which option you're interested in (1 or 2)
   - Best time to connect this week

We'll have your system live and reducing no shows within 7 days.

---

*Questions? Reply to this email or call/text [your phone number].*
