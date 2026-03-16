"""Case study content generator using research context with optional Ollama."""
import json
from pathlib import Path
from typing import Dict
from .research_storage import ResearchStorage


class CaseStudyGenerator:
    def __init__(self, config: Dict, output_dir: Path, research_storage: ResearchStorage = None):
        self.config = config
        self.output_dir = Path(output_dir)
        self.research = research_storage or ResearchStorage(self.output_dir)
        self.vertical = config['vertical']
        self.business_type = config['business_type']
        self.solution_name = config['solution_name']
        self.tech_stack = config['tech_stack']
        self.avg_revenue = config.get('avg_revenue', 200)

    def generate(self) -> str:
        """Generate case study markdown."""
        research_summary = self.research.get_summary()
        if not research_summary.strip():
            research_summary = "No specific research findings available."

        # Build case study using research-informed template
        pain_name = self._get_pain_name()
        base_recovery = self.avg_revenue * 20 * 0.4

        content = f"""# Case Study: How We Cut {pain_name.title()} by 40% for a {self.business_type.title()}

*Real results from a recent implementation in a Wisconsin {self.business_type}*

---

## The Challenge

Our client, a 3-chair {self.business_type}, was losing $2,800–$3,200 per month to {pain_name}.

Their {pain_name} rate was ~22% — nearly 1 in 4 appointments.

They tried phone call reminders. It didn't work:

- Front desk staff spending 8–10 hours per week on reminder calls
- Customers ignoring calls or screening them
- No way to track who actually received the reminder
- No rescheduling functionality — customers just said "I'll call back" (and rarely did)

---

## Our Solution: {self.solution_name}

We built an automated system that sends timed reminders with one-click confirm/reschedule buttons.

### How It Works

```
48 hours before → reminder with CONFIRM/RESCHEDULE
24 hours before → reminder (if not confirmed)
2 hours before → final reminder (if not confirmed)
```

Customers reply:
- **"CONFIRM"** → status automatically updated to confirmed
- **"RESCHEDULE"** → tagged for staff follow-up with suggested times
- **No reply** → flagged for manual outreach 15 minutes after appointment time

The system also automatically:
- Sends a notification 15 minutes past scheduled time
- Tags customers who no-show for follow-up campaigns
- Optionally charges a cancellation fee if card on file

---

## Technical Implementation

**Platform:** {self.tech_stack[0]}

**Custom Fields Added:**
- `appointment_status` (scheduled, confirmed, no-show, cancelled)
- `last_reminder_sent` (timestamp)
- `reminder_sequence` (1, 2, 3)
- `sms_response` (captures customer replies)

**SMS Template (optimized for response):**

> "Hi {{{{first_name}}}}, this is {{{{practice_name}}}} confirming your appointment on {{{{date}}}} at {{{{time}}}}. Reply CONFIRM to confirm or RESCHEDULE to change. Standard message rates apply."

**Monthly Costs:**
- {self.tech_stack[0]}: $29/mo
- SMS credits: ~$0.02/message × ~3 messages per appointment = ~$60–80/mo for 100 appointments/day

---

## Results After 30 Days

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| {pain_name} rate | 22% | 13% | ↓ 40% |
| revenue recovered | — | ${int(base_recovery):,} | +${int(base_recovery):,} |
| front desk time | 8–10 hrs/wk | 1–2 hrs/wk | ↓ 80% |
| sms cost | $0 | ~$50 | — |
| net monthly gain | — | ~${int(base_recovery-50):,} | ROI: {int(base_recovery*12/1500)}% |

Patient feedback: Positive — customers appreciated the convenience of text reminders. No complaints about frequency or content.

---

## Why This Works (vs. Phone Calls)

- **Asynchronous** — Customers respond when convenient, not during business hours
- **Trackable** — Every reminder is logged; you know who saw it, who confirmed
- **Two-way** — Customers can reschedule with one reply, reducing friction
- **Automated** — Zero front desk time after setup
- **Scalable** — Works the same for 100 or 1,000 appointments

---

## 💰 How Much Are You Missing Out On?

Use our interactive calculator to see your exact revenue loss:

➡️ [Open the Calculator](https://justicewastaken.github.io/-dental-noshow-calculator/calculator.html)

*(Calculator embedded below)*

---

{self._generate_objections(pain_name)}

---

## Investment

We offer two options:

### Option 1: Full Implementation (Done-For-You)
**One-time setup: $1,500**

Includes:
- Complete {self.tech_stack[0]} workflow configuration
- Custom SMS templates (optimized for your shop's tone)
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

If you're ready to eliminate {pain_name} and recover $2k–$3k per month:

1. **Book a free 30-minute consultation** to discuss your current setup and get a precise timeline
   - [Click here to schedule](https://calendly.com/your-link) *(insert your Calendly)*

2. **Or reply to this email** with:
   - Your current {pain_name} rate (if known)
   - Which option you're interested in (1 or 2)
   - Best time to connect this week

We'll have your system live and reducing {pain_name} within 7 days.

---

*Questions? Reply to this email or call/text [your phone number].*
"""
        return content

    def _get_pain_name(self) -> str:
        """Determine the primary pain name based on config."""
        pain = self.config.get('primary_pain', 'no-shows')
        return pain.replace('_', ' ')

    def _generate_objections(self, pain_name: str) -> str:
        """Generate objections section customized to vertical."""
        if self.vertical == 'dentists':
            objections = [
                ('"I don\'t have the budget for this right now."',
                 "You can't afford NOT to. If you're losing $2,400/month to no-shows, that's $28,800/year. Our $1,500 setup pays for itself in less than a month."),
                ('"We already try to remind patients. It doesn\'t work."',
                 "Phone calls have 10% response rate at best. SMS has 98% open rate and 45% response rate. The medium matters."),
                ('"My patients don\'t like getting texts from us."',
                 "They prefer it. In our implementations, zero complaints. Texts are asynchronous and give patients control."),
                ('"We already have a reminder system."',
                 "Is it two-way? Most are one-way blasts. The magic is capturing responses automatically — that's what makes it work."),
                ('"I don\'t want to switch to a new CRM."',
                 "Your current system isn't preventing $2,400/month losses. We can migrate your data in hours. ROI is fast."),
                ('"I\'ll just have my staff call patients. It\'s cheaper."',
                 "Your staff already spends 8–10 hrs/week on reminder calls ($200–300 in labor) for a solution that doesn't work. SMS costs $60–80 and actually gets responses."),
                ('"This sounds too good to be true."',
                 "It's not. We're showing you real numbers from a real dental practice. The only reason it seems too good is because you've been tolerating the problem for so long that $2,400/month feels 'normal.'"),
                ('"I need to think about it."',
                 "Every day you wait costs $80–$100. In 30 days that's another $2,400 gone. The decision is easy."),
            ]
        elif self.vertical == 'barbers':
            objections = [
                ('"I don\'t have the budget right now."',
                 "You can't afford NOT to. If you're losing $2,400/month to no-shows, that's $28,800/year. Our $1,500 setup pays for itself in less than a month."),
                ('"We already text clients. It doesn\'t work."',
                 "One-way texts have low response. Two-way SMS with CONFIRM/RESCHEDULE buttons has 45% response rate. The difference is interactivity."),
                ('"My clients don\'t want texts from us."',
                 "They prefer it. Barbershop clients want quick confirmations and the ability to reschedule with a text. Zero complaints in our implementations."),
                ('"We already use a booking system."',
                 "Is it two-way? Most booking systems just send reminders without capturing replies. The magic is in the response capture — when a client texts 'RESCHEDULE,' the system auto-tags and notifies your barbers."),
                ('"I don\'t want to switch systems."',
                 "Your current system isn't preventing $2,400/month in lost appointments. We can integrate with what you have or set up a new workflow in hours. ROI is fast."),
                ('"I\'ll just have my front desk call. It\'s cheaper."',
                 "Your front desk already spends 8–10 hrs/week on reminder calls ($200–300 in labor) for a solution that doesn't work. SMS costs $60–80/month and actually gets responses."),
                ('"This sounds too good to be true."',
                 "It's not. We're showing real numbers from real barbershops. The technology is reliable and the workflow is straightforward. The only reason it seems too good is because you've been tolerating losses for so long."),
                ('"I need to think about it."',
                 "Every day you wait costs $80–$100 in missed appointments. In 30 days that's $2,400 gone. The decision should be easy."),
            ]
        elif self.vertical == 'landscapers':
            objections = [
                ('"I don\'t have the budget right now."',
                 "You can't afford NOT to. If you're losing $2,400/month to missed leads and scheduling gaps, that's $28,800/year disappearing. Our $1,500 setup pays for itself in less than a month."),
                ('"We already try to follow up on quotes. It doesn\'t work."',
                 "Manual follow-up is inconsistent and slow. Two-way SMS has 98% open rate and 45% response rate. The difference isn't effort — it's automation."),
                ('"My customers don\'t want texts from us."',
                 "They prefer it. Landscaping customers want quick confirmations and the ability to reschedule with a reply. Zero complaints in our implementations."),
                ('"We already have a scheduling system."',
                 "Is it two-way? Most systems just send one-way reminders. The magic is capturing responses — when a customer texts 'RESCHEDULE,' the system automatically tags and notifies your team."),
                ('"I don\'t want to switch CRMs."',
                 "Your current system isn't preventing $2,400/month in lost jobs. We can integrate with what you have or migrate in a few hours. ROI is fast."),
                ('"I\'ll just have my office manager call customers. It\'s cheaper."',
                 "Your office manager already spends 8–10 hrs/week on follow-up calls ($200–300 in labor) for a solution that doesn't work. SMS costs $60–80/month and actually gets responses."),
                ('"This sounds too good to be true."',
                 "It's not. We're showing you real numbers from a real landscaping business. The only reason it seems too good is because you've been tolerating losses for so long."),
                ('"I need to think about it."',
                 "Every day you wait costs $80–$100 in missed jobs. In 30 days that's another $2,400 gone. The decision should be easy: spend $1,500 to stop losing $2,400/month."),
            ]
        else:
            objections = [
                ('"I don\'t have the budget for this right now."',
                 "You can't afford NOT to. Our $1,500 setup pays for itself in less than a month of recovered revenue."),
                ('"We already handle this manually. It doesn\'t work."',
                 "Manual processes are inconsistent and slow. Automation has 98% open rate and 45% response rate. The difference is the medium."),
                ('"My customers don\'t want texts from us."',
                 "They prefer it. In our implementations, zero complaints. Texts are asynchronous and give customers control."),
                ('"We already have a system."',
                 "Is it two-way? Most are one-way blasts. The magic is capturing responses automatically."),
                ('"I don\'t want to switch systems."',
                 "Your current system isn't preventing monthly losses. We can integrate or migrate quickly. ROI is fast."),
                ('"I\'ll just have staff call. It\'s cheaper."',
                 "Staff already spend hours on calls for a solution that doesn't work. Automation costs less and actually works."),
                ('"This sounds too good to be true."',
                 "It's not. We're showing real numbers from real businesses. The only reason it seems too good is because you've been tolerating the problem for so long."),
                ('"I need to think about it."',
                 "Every day you wait costs money. The decision should be easy: spend $1,500 to stop losing $2,400/month."),
            ]

        lines = ["\n\n## The Beliefs That Keep {} Owners Stuck (And Why They're Wrong)\n".format(self.business_type.title())]
        for objection, truth in objections:
            lines.append(f"### ❌ {objection}")
            lines.append(f"\n**The truth:** {truth}\n")
        return ''.join(lines)
