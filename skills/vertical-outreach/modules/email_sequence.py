"""Email sequence builder."""
from datetime import datetime


class EmailSequenceBuilder:
    def __init__(self, config, case_study_url, calculator_url, leads_csv=None):
        self.config = config
        self.case_study_url = case_study_url
        self.calculator_url = calculator_url
        self.leads_csv = leads_csv
        self.business_type = config['business_type']
        self.vertical = config['vertical']

    def generate_sequence(self) -> list:
        """Generate 3-email sequence."""
        return [
            self._email_1(),
            self._email_2(),
            self._email_3()
        ]

    def _email_1(self) -> str:
        return f"""Subject: Quick question about {{practice_name}}'s appointment reminders

Hey {{dentist_name}},

I noticed {{practice_name}} in {{city}} and wanted to reach out about something I keep hearing from {self.business_type}s: the struggle with appointment no-shows.

We just helped a 3-chair {self.business_type} in Wisconsin cut their no-show rate by 40% — going from 22% to 13% in 30 days — without increasing staff workload.

The solution was surprisingly simple: two-way SMS reminders instead of phone calls.

I documented the entire system in a short case study:
{self.case_study_url}

It covers exactly how they set it up in GoHighLevel and the results they've been seeing.

If you're already using a reminder system that works, great — I don't want to waste your time.

But if you're still doing manual calls or one-way texts, this might be worth 10 minutes of your day.

Brief questions? Just hit reply.

Best,
Justice
Forward Commerce
"""

    def _email_2(self) -> str:
        return f"""Subject: Following up: {{practice_name}} no-show calculator

Hey {{dentist_name}},

Following up on my last email about reducing no-shows.

I also built a quick calculator that shows exactly how much revenue you're losing based on your practice metrics:

{self.calculator_url}

Plug in your numbers (appointments per month, avg revenue, current no-show rate) and it'll tell you:

- Current monthly loss
- Projected loss after 40% reduction
- Revenue recovered per month
- Payback period for our solution

For the Wisconsin practice we worked with, it showed a $22,000 monthly loss. After implementing, they're recovering about $8,800/month.

Might be worth checking out if you haven't already.

Let me know if you'd like to discuss how this could work for {{practice_name}}.

Best,
Justice
"""

    def _email_3(self) -> str:
        return f"""Subject: Last attempt: {{practice_name}} no-show solution

Hey {{dentist_name}},

One last email — I know you're busy.

We've now implemented this no-show automation for several {self.business_type}s, and the results are consistent: 30-50% reduction in missed appointments within the first month.

The investment is $1,500 one-time (or $500/mo for ongoing management), and most practices recover their entire investment within 3-4 weeks.

If you're interested in exploring this for {{practice_name}}, let's schedule a quick 30-minute call to:

- Review your current setup
- Run the numbers for your specific practice
- Show you exactly how the system works

[Click here to book a time that works for you](https://calendly.com/your-link)

If not, no worries — I won't bother you again.

Either way, I hope you get your no-shows under control soon.

Best,
Justice
"""
