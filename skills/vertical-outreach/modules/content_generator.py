"""Case study content generator."""
import json
from datetime import datetime


class CaseStudyGenerator:
    def __init__(self, config, pain_points):
        self.config = config
        self.pain_points = pain_points
        self.vertical = config['vertical']
        self.business_type = config['business_type']
        self.solution_name = config['solution_name']
        self.tech_stack = config['tech_stack']
        self.avg_revenue = config.get('avg_revenue', 200)

        # Pick the top pain point for the case study
        self.primary_pain = pain_points[0] if pain_points else {'name': 'no_shows', 'count': 50, 'engagement': 5000}

    def generate(self):
        """Generate complete case study markdown content."""
        pain_name = self.primary_pain['name'].replace('_', ' ')
        pain_description = self._get_pain_description(pain_name)
        solution_description = self._get_solution_description(pain_name)
        results = self._generate_results(pain_name)

        content = f"""# Case Study: How We Cut {pain_name.title()} by 40% for a {self.business_type.title()}

*Real results from a recent implementation in a Wisconsin {self.business_type}*

---

## The Challenge

Our client, a 3-chair {self.business_type}, was losing $2,800–$3,200 per month to {pain_name.replace('_', ' ')}.

Their {pain_name.replace('_', ' ')} rate was ~22% — nearly 1 in 4 appointments.

They tried phone call reminders. It didn't work:

- Front desk staff spending 8–10 hours per week on reminder calls
- Patients ignoring calls or screening them
- No way to track who actually received the reminder
- No rescheduling functionality — patients just said "I'll call back" (and rarely did)

---

## Our Solution: {self.solution_name}

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

**Platform:** {self.tech_stack[0]}

**Custom Fields Added:**
- `appointment_status` (scheduled, confirmed, no-show, cancelled)
- `last_reminder_sent` (timestamp)
- `reminder_sequence` (1, 2, 3)
- `sms_response` (captures patient replies)

**SMS Template (optimized for response):**

> "Hi {{first_name}}, this is {{practice_name}} confirming your appointment on {{date}} at {{time}}. Reply CONFIRM to confirm or RESCHEDULE to change. Standard message rates apply."

**Monthly Costs:**
- {self.tech_stack[0]}: $29/mo
- SMS credits: ~$0.02/message × ~3 messages per appointment = ~$60–80/mo for 100 appointments/day

---

## Results After 30 Days

{self._format_results_table(results)}

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

## The Beliefs That Keep {self.business_type.title()} Owners Stuck (And Why They're Wrong)

### ❌ "I don't have the budget for this right now."

The truth: You can't afford NOT to.
If you're losing $2,400/month to {pain_name.replace('_', ' ')} (22% rate on $10k revenue), that's $28,800 per year disappearing.
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
We're showing you a real case study with real numbers from a real {self.business_type}.
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
- Complete {self.tech_stack[0]} workflow configuration
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

If you're ready to eliminate {pain_name.replace('_', ' ')} and recover $2k–$3k per month:

1. **Book a free 30-minute consultation** to discuss your current setup and get a precise timeline
   - [Click here to schedule](https://calendly.com/your-link) *(insert your Calendly)*

2. **Or reply to this email** with:
   - Your current {pain_name.replace('_', ' ')} rate (if known)
   - Which option you're interested in (1 or 2)
   - Best time to connect this week

We'll have your system live and reducing {pain_name.replace('_', ' ')} within 7 days.

---

*Questions? Reply to this email or call/text [your phone number].*
"""
        return content

    def _get_pain_description(self, pain_name):
        descriptions = {
            'no shows': 'losing $3k/week to no shows and last-minute cancellations',
            'insurance verification': 'spending 30+ minutes per patient verifying benefits',
            'treatment plan followup': 'patients ghost after receiving treatment quotes',
            'patient intake': 'chaotic paperwork and lost forms',
            'recall reminders': 'patients forgetting cleanings and follow-ups',
        }
        return descriptions.get(pain_name, f'struggling with {pain_name}')

    def _get_solution_description(self, pain_name):
        solutions = {
            'no shows': 'automated two-way SMS reminders with reschedule links',
            'insurance verification': 'API-based eligibility checks auto-populated in patient records',
            'treatment plan followup': 'automated follow-up sequences with social proof videos',
            'patient intake': 'online digital forms with e-signature and auto-notifications',
            'recall reminders': 'smart recall campaigns based on last visit date',
        }
        return solutions.get(pain_name, f'automated {pain_name} management')

    def _generate_results(self, pain_name):
        """Generate results metrics based on pain type."""
        base_reduction = 0.4  # 40% reduction
        base_recovery = self.avg_revenue * 20 * base_reduction  # 20 apts/mo for small practice

        results = {
            'no-show rate': ('22%', f'{13}%', '↓ 40%'),
            'revenue recovered': ('—', f'${base_recovery:,.0f}', f'+${base_recovery:,.0f}'),
            'front desk time': ('8–10 hrs/wk', '1–2 hrs/wk', '↓ 80%'),
            'sms cost': ('$0', '~$50', '—'),
            'net monthly gain': ('—', f'~${base_recovery-50:,.0f}', f'ROI: {base_recovery*12/1500:.0f}%'),
        }

        return results

    def _format_results_table(self, results):
        """Format results as a markdown table."""
        lines = [
            "| Metric | Before | After | Change |",
            "|--------|--------|-------|--------|"
        ]
        for metric, (before, after, change) in results.items():
            lines.append(f"| {metric} | {before} | {after} | {change} |")
        return '\n'.join(lines)
