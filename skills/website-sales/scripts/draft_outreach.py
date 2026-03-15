#!/usr/bin/env python3
"""
Generate personalized outreach emails for leads.
Templates located in references/email-templates.md
"""

import argparse
import json
import os
import sys
from datetime import datetime

# Load email templates
TEMPLATES = {
    'initial': """Subject: UW-Eau Claire student building salon websites

Hey {owner_name},

I came across {business_name} while looking for salons in {city} and noticed you're using {booking_platform} for booking. I'd love to build you a proper website that integrates with your {booking_platform} system—something that showcases your work beyond just the booking page.

I'm a UW-Eau Claire student building my portfolio, so I'd create a custom site for you at a student rate. We could hop on a quick call and I'd show you exactly what I'm thinking.

If it's not a fit, no hard feelings—just trying to get some real experience under my belt.

Let me know if you're interested.

Best,
Justice
715-308-7949
{portfolio_url}""",

    'followup-3d': """Subject: Following up: {business_name} website

Hi {owner_name},

Just wanted to follow up on my email about creating a new website for {business_name}. I'm still excited about the possibility of working with you and can have a draft ready within a week if you're interested.

Any thoughts?

Best,
Justice""",

    'followup-7d': """Subject: One more: {business_name} website idea

Hi {owner_name},

I know you're busy, but I wanted to share a quick example of a website I recently built for a similar {industry} business: [EXAMPLE LINK]

If you'd like something like this for {business_name}, I'm offering a special rate this month. Let me know if you want to chat for 15 minutes.

Best,
Justice""",

    'followup-14d': """Subject: Final: {business_name} website opportunity

Hi {owner_name},

This is my last email about the website offer. I want to make sure I'm not pushing too hard, but I genuinely believe I can create something that will help {business_name} attract more customers.

If you're interested, hit reply and we'll set up a quick call. If not, no worries at all—I appreciate your time either way.

All the best,
Justice"""
}

def load_leads(leads_file):
    with open(leads_file, 'r') as f:
        return json.load(f)

def substitute(template, context):
    """Replace placeholders in template with context values."""
    result = template
    for key, value in context.items():
        placeholder = '{' + key + '}'
        result = result.replace(placeholder, str(value) if value else '')
    return result.strip()

def generate_emails(leads, template_type='initial', portfolio_url=None, your_phone=None, setup_price=None, example_link=None):
    """Generate email drafts for all leads."""
    emails = []
    template = TEMPLATES.get(template_type, TEMPLATES['initial'])

    for lead in leads:
        # Build context for substitution
        # Support both 'name' (old) and 'business_name' (our CSV) keys
        business_name = lead.get('name') or lead.get('business_name') or 'Business'
        owner_name = lead.get('owner_name') or lead.get('owner_first_name') or 'there'
        current_website = lead.get('website') or lead.get('current_website') or ''
        industry = lead.get('industry', 'local business')
        context = {
            'business_name': business_name,
            'owner_name': owner_name,
            'current_website': current_website,
            'industry': industry,
            'city': lead.get('city', 'your area'),
            'booking_platform': lead.get('booking_platform', 'a booking system'),
            'portfolio_url': portfolio_url or 'YOUR_PORTFOLIO_LINK',
            'your_phone': your_phone or 'YOUR_PHONE',
            'setup_price': setup_price or 'X',
            'example_link': example_link or portfolio_url or 'YOUR_EXAMPLE_LINK'
        }

        email_body = substitute(template, context)
        email = {
            'to': lead.get('email'),
            'subject': email_body.split('\n')[0].replace('Subject: ', '').strip(),
            'body': '\n'.join(email_body.split('\n')[1:]).strip(),
            'lead_name': lead.get('name'),
            'lead_id': lead.get('id', lead.get('name', '').lower().replace(' ', '-')),
            'template': template_type
        }
        emails.append(email)

    return emails

def main():
    parser = argparse.ArgumentParser(description='Draft personalized outreach emails for leads.')
    parser.add_argument('--leads', required=True, help='Leads JSON file from find-leads')
    parser.add_argument('--template', default='initial', choices=['initial', 'followup-3d', 'followup-7d', 'followup-14d'], help='Email template type')
    parser.add_argument('--portfolio-url', help='Your portfolio website URL')
    parser.add_argument('--your-phone', help='Your phone number')
    parser.add_argument('--setup-price', help='Setup fee amount (to include in email)')
    parser.add_argument('--example-link', help='Example website you built (for 7-day followup)')
    parser.add_argument('--output', default='emails.json', help='Output JSON file')
    args = parser.parse_args()

    # Load leads
    leads = load_leads(args.leads)

    # Filter leads with email addresses only
    leads_with_email = [l for l in leads if l.get('email')]
    if len(leads_with_email) < len(leads):
        print(f"Warning: {len(leads) - len(leads_with_email)} leads missing email addresses.", file=sys.stderr)

    print(f"Generating {args.template} emails for {len(leads_with_email)} leads...")
    emails = generate_emails(leads_with_email, args.template, args.portfolio_url, args.your_phone, args.setup_price, args.example_link)

    # Save
    with open(args.output, 'w') as f:
        json.dump(emails, f, indent=2)

    print(f"✓ Saved {len(emails)} emails to {args.output}")
    print(f"\nPreview (first email):")
    print(f"To: {emails[0]['to']}")
    print(f"Subject: {emails[0]['subject']}")
    print(f"Body:\n{emails[0]['body'][:300]}...")

    print("\nNext steps:")
    print("  1. Review emails.json")
    print("  2. Dry run: website-sales send-emails --emails emails.json --dry-run")
    print("  3. Send: website-sales send-emails --emails emails.json")

if __name__ == '__main__':
    main()
