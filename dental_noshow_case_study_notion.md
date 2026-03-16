# Case Study: How We Cut No-Shows by 40% for a Dental Clinic

*Real results from a recent implementation in a Wisconsin dental practice*

---

## 📊 The Challenge

Our client, a 3-chair dental practice in Wisconsin, was losing **$2,800–$3,200 per month** to no-shows and last-minute cancellations.

Their no-show rate was **22%** — nearly 1 in 4 appointments.

They tried phone call reminders. It didn't work:
- Front desk staff spending 8–10 hours per week on reminder calls
- Patients ignoring calls or screening them
- No way to track who actually received the reminder
- No rescheduling functionality — patients just said "I'll call back" (and rarely did)

They needed a solution that:
- Reduced no-shows without increasing staff workload
- Was trackable and automated
- Allowed patients to confirm/reschedule themselves
- Integrated with their existing GoHighLevel scheduler

---

## ✅ Our Solution: Two-Way SMS Automation

We built an automated two-way SMS reminder system in GoHighLevel that sends timed reminders with **one-click confirm/reschedule buttons**.

### How It Works

```
48 hours before → SMS reminder with CONFIRM/RESCHEDULE
24 hours before → SMS reminder (if not confirmed)
2 hours before → Final reminder (if not confirmed)
```

Patients reply:
- **"CONFIRM"** → status automatically updated to confirmed
- **"RESCHEDULE"** → tagged for staff follow-up with suggested times
- **No reply** → flagged for manual outreach 15 minutes after appointment time

The system also automatically:
- Sends a no-show notification 15 minutes past scheduled time
- Tags patients who no-show for follow-up campaigns
- Optionally charges a $50 cancellation fee if card on file

---

## 🛠 Technical Implementation

**Platform:** GoHighLevel (GHL Solo)

**Custom Fields Added:**
- `appointment_status` (scheduled, confirmed, no-show, cancelled)
- `last_reminder_sent` (timestamp)
- `reminder_sequence` (1, 2, 3)
- `sms_response` (captures patient replies)

**Workflow Structure:**
1. **Trigger:** Appointment scheduled/rescheduled
2. **Wait until** 48h, 24h, 2h before appointment
3. **Send SMS** with two-way response capture
4. **Branch logic** based on patient reply
5. **No-show workflow** fires if status never changes

**SMS Template (optimized for response):**

> "Hi {{first_name}}, this is {{practice_name}} confirming your appointment on {{date}} at {{time}}. Reply CONFIRM to confirm or RESCHEDULE to change. Standard message rates apply."

**Integration Details:**
- Works with any GHL calendar/scheduler
- No additional software costs (GHL Solo = $29/mo)
- SMS credits: ~$0.02 per outbound message
- Average 3 messages per appointment = ~$0.06/apt

---

## 📈 Results After 30 Days

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| No-show rate | 22% | 13% | ↓ 40% |
| Revenue recovered (monthly) | — | $2,400 | +$2,400 |
| Front desk time spent on reminders | 8–10 hrs/wk | 1–2 hrs/wk | ↓ 80% |
| SMS cost | $0 | ~$50 | — |
| **Net monthly gain** | — | **~$2,350** | ROI: 4,600% |

**Patient feedback:** Positive — patients appreciated the convenience of text reminders. No complaints about frequency or content.

---

## 💡 Why This Approach Works (vs. Phone Calls)

1. **Asynchronous** — Patients respond when it's convenient, not during business hours
2. **Trackable** — Every reminder is logged; you know who saw it, who confirmed
3. **Two-way** — Patients can reschedule with one reply, reducing friction
4. **Automated** — Zero front desk time after setup
5. **Scalable** — Works the same for 100 or 10,000 patients

The dental community on Reddit consistently recommends SMS as the #1 solution for no-shows. Our implementation follows the exact patterns discussed in r/dentistry and r/dentists.

---

## 🎯 Is This Right for Your Practice?

This solution is ideal if you:
- Have 15%+ no-show rate
- Are tired of staff playing phone tag
- Want a trackable, automated system
- Already use GoHighLevel (or are willing to switch)
- Want results in under 2 weeks

**Not ideal if:**
- Your no-show rate is already <5% (you're exceptional)
- You don't use any CRM/scheduling software (but we can help with that)
- You prefer in-person reminders only (old school)

---

## 💰 Investment

We offer two options:

### Option 1: Full Implementation (Done-For-You)
- **One-time setup:** $1,500
- **Includes:**
  - Complete GHL workflow configuration
  - Custom SMS templates (optimized for your practice tone)
  - Integration with your existing appointment calendar
  - Testing with 10–20 appointments to ensure flawless operation
  - 30 days of support (tweaks, adjustments, troubleshooting)
  - Documentation and 1-hour staff training session

**Timeline:** 3–5 days from start to live

---

### Option 2: Ongoing Management
If you want us to handle everything:

- **Monthly fee:** $500/mo
  - Full system monitoring
  - Monthly optimization based on performance data
  - SMS template tweaks and A/B testing
  - Report on no-show metrics and revenue recovered
  - Priority support

*First-time clients often start with Option 1 and add Option 2 after seeing the results.*

---

## 📋 What We Need From You

1. **Access to your GoHighLevel account** (or we'll set up a new one)
2. **Current appointment calendar** (to integrate with)
3. **SMS sending capacity** (GHL provides this, just ensure you have credits)
4. **30-minute kickoff call** to understand your current workflow and branding

That's it. We handle the rest.

---

## 📞 Next Steps

**If you're ready to eliminate no-shows and recover $2k–$3k per month:**

1. **Book a free 30-minute consultation** to discuss your current setup and get a precise timeline
   - [Click here to schedule](https://calendly.com/your-link) *(insert your Calendly)*

2. **Or reply to this email** with:
   - Your current no-show rate (if known)
   - Which option you're interested in (1 or 2)
   - Best time to connect this week

We'll have your system live and reducing no-shows within 7 days.

---

## ❓ Frequently Asked Questions

**Do we need to switch to GoHighLevel?**  
If you're not on GHL, yes — the automation is built there. GHL Solo is $29/mo and includes SMS capabilities. We can migrate your data.

**What if patients don't reply to texts?**  
They get the 2-hour reminder, then if they still don't confirm, they're flagged for manual outreach 15 minutes after their scheduled time. The system still notifies you of potential no-shows.

**Can we customize the timing?**  
Yes. Common setups: 72h + 24h + 2h, or 48h + 24h + 2h. We'll test what works best for your patient demographic.

**What about HIPAA compliance?**  
GHL is HIPAA-compliant. SMS content is minimal (appointment reminder only). No PHI in messages.

**Do you charge per text?**  
SMS costs are separate (~$0.02/message). For a 20-doctor practice with 100 appointments/day, expect ~$120/month in SMS fees. We optimize to minimize this.

**What if we already have a reminder system?**  
We'll evaluate it. Often existing systems are one-way only or lack the response capture that makes this work. Our system is specifically built for two-way engagement.

---

## 🎉 Ready to Cut Your No-Shows?

We've built this exact system for a dental practice and delivered the results above. Now we can do the same for you.

Space is limited — we only take on 3–4 new clients per month to ensure quality implementation.

**[Book your free consultation now](https://calendly.com/your-link)** and let's get your no-show rate under 15% in the next 30 days.

---

*Questions? Reply to this email or call/text [your phone number].*
