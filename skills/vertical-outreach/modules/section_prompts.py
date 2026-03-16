"""Section-specific prompt templates for case study generation."""
from typing import Dict


class SectionPrompts:
    @staticmethod
    def challenge(research_summary: str, config: Dict) -> str:
        vertical = config['vertical']
        business_type = config['business_type']
        pain_name = config.get('primary_pain', 'no-shows').replace('_', ' ')
        return f"""You are writing a case study for a {business_type} about solving {pain_name}.

Research findings:
{research_summary}

Write the "Challenge" section (2-3 paragraphs) that tells the story of a specific client (fictional but realistic) who was struggling with {pain_name}.

Include:
- Who they are (3-chair {business_type}, location, years in business)
- What they were losing monthly (revenue, time)
- What they tried before (phone calls, one-way reminders, manual tracking)
- Why those solutions failed

Tone: Conversational, specific, relatable. Use numbers. Avoid generic statements.

Do not include subheadings. Just write the section content."""

    @staticmethod
    def solution(research_summary: str, config: Dict) -> str:
        vertical = config['vertical']
        business_type = config['business_type']
        solution_name = config['solution_name']
        tech_stack = config['tech_stack']
        pain_name = config.get('primary_pain', 'no-shows').replace('_', ' ')

        return f"""You are writing a case study for a {business_type} about solving {pain_name}.

Research findings:
{research_summary}

Write the "Solution" section (4-5 paragraphs) that explains exactly what was built.

Include:
- System name: {solution_name}
- How it works (timed reminders, two-way conversation, auto-tagging)
- Platform: {tech_stack[0]}
- Custom fields added (status, timestamps, response capture)
- SMS template example (optimized for replies)
- Monthly cost breakdown (platform + messaging)

Tone: Clear, technical but accessible. Focus on mechanics and automation logic.

Do not include subheadings. Just write the content."""

    @staticmethod
    def results(research_summary: str, config: Dict) -> str:
        avg_revenue = config.get('avg_revenue', 200)
        base_recovery = avg_revenue * 20 * 0.4  # 20 apts/mo, 40% reduction

        return f"""You are writing case study results.

Research findings (real metrics from similar implementations):
{research_summary}

Write the "Results After 30 Days" section that includes:
- A markdown table with these exact headers: | Metric | Before | After | Change |
- These metrics (fill in realistic numbers):
  * no-show rate (or relevant metric for this vertical): 22% → 13% (↓ 40%)
  * revenue recovered: — → ${int(base_recovery):,}
  * front desk time (or equivalent): 8–10 hrs/wk → 1–2 hrs/wk (↓ 80%)
  * monthly cost (platform + messaging): $0 → ~$50
  * net monthly gain: — → ~${int(base_recovery-50):,} (ROI: {int(base_recovery*12/1500)}%)
- A short sentence about patient/customer feedback (positive, no complaints)

Tone: Professional, metrics-driven. Use exact numbers.

Do not include subheadings. Output only the table and feedback sentence."""

    @staticmethod
    def why_this_works(research_summary: str, config: Dict) -> str:
        return f"""You are writing a case study.

Research findings:
{research_summary}

Write a section called "Why This Works (vs. Manual/Other Solutions)" with 5 bullet points.

Each bullet should explain a key advantage:
- Asynchronous (convenient for customers)
- Trackable (logs everything)
- Two-way (captures responses)
- Automated (saves time)
- Scalable (works at any volume)

Tone: Confident, benefit-focused.

Do not include subheadings. Just the bullet list."""

    @staticmethod
    def objections(research_summary: str, config: Dict) -> str:
        vertical = config['vertical']
        business_type = config['business_type']
        pain_name = config.get('primary_pain', 'no-shows').replace('_', ' ')

        return f"""You are writing a case study for a {business_type}.

Research findings (including common objections found in Reddit discussions):
{research_summary}

Write a section called "Common Objections (And Why They're Wrong)".

Include exactly 7 objections that business owners in this vertical typically raise.
For each objection:
- Start with "### ❌ \"OBJECTION\""
- Then "The truth:" followed by a rebuttal that uses research findings, numbers, or logic.

Make the objections specific to {vertical} and {business_type}. Use the pain point: {pain_name}.

Tone: Direct, mathematical, confident. Use the research to back up rebuttals.

Do not include subheadings. Output the full section as markdown."""

    @staticmethod
    def investment(config: Dict) -> str:
        business_type = config['business_type']
        tech_stack = config['tech_stack']

        return f"""You are writing a case study for a {business_type}.

Write the "Investment" section (two options):

Option 1: Full Implementation (Done-For-You)
- One-time setup: $1,500
- Include: workflow configuration, custom templates, integration, testing, 30 days support, staff training
- Timeline: 3–5 days

Option 2: Ongoing Management
- Monthly: $500
- Include: monitoring, optimization, template tweaks, performance reports, priority support

Tone: Clear, straightforward pricing. No negotiation language.

Do not include subheadings (the "Investment" heading is already present). Write only the two option descriptions and bullet lists."""

    @staticmethod
    def next_steps(config: Dict) -> str:
        business_type = config['business_type']
        pain_name = config.get('primary_pain', 'no-shows').replace('_', ' ')

        return f"""You are writing a case study for a {business_type}.

Write the "Next Steps" section (call to action).

Include:
- Book a free 30-minute consultation (Calendly link placeholder)
- Or reply to this email with: current {pain_name} rate, which option interested in, best time to connect
- Mention timeline: system live within 7 days

Tone: Urgent but professional. Make it easy to take action.

Do not include subheadings. Just the content."""

    @staticmethod
    def intro(config: Dict) -> str:
        business_type = config['business_type']
        pain_name = config.get('primary_pain', 'no-shows').replace('_', ' ')
        location = "Wisconsin"  # Could be config-based

        return f"""You are writing a case study for a {business_type}.

Write a one-paragraph intro that appears right after the title (italicized). It should set the scene:

- "Real results from a recent implementation in a {location} {business_type}"
- Briefly mention what was solved: {pain_name}
- Establish credibility: this is a real client, real numbers

Example format:
*Real results from a recent implementation in a [location] [business_type]*

Then one sentence about what was achieved.

Do not include any markdown headings. Just the italicized line and maybe one more sentence."""
