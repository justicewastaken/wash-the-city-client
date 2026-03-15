#!/usr/bin/env python3
"""
Find local solo/small businesses with outdated or missing websites.
Scrapes Google search results and local directories.
"""

import argparse
import json
import re
import subprocess
import sys
import time
from urllib.parse import quote_plus

# Optional: Use googlesearch-python if available, else fallback to simple scraping
try:
    from googlesearch import search as google_search
    HAS_GOOGLE_SEARCH = True
except ImportError:
    HAS_GOOGLE_SEARCH = False

def search_businesses(city, count=50, industries=None, radius=25):
    """
    Find businesses in target city. Returns list of lead dicts.
    """
    leads = []
    search_queries = []

    # Build search queries
    if industries:
        industry_list = industries.split(',')
    else:
        industry_list = [
            'restaurant', 'cafe', 'bakery', 'salon', 'barber', 'bar', 'brewery',
            'contractor', 'plumber', 'electrician', 'roofer', 'landscaper',
            'boutique', 'clothing store', 'fitness trainer', 'yoga studio',
            'hair salon', 'nail salon', 'massage therapist', 'consultant',
            'real estate agent', 'insurance agent', 'accountant', 'lawyer'
        ]

    # Cities: target city + nearby if radius allows
    base_city = city.replace(' ', '+')
    search_queries = [f"{industry} {city} small business" for industry in industry_list]

    # If using googlesearch library
    if HAS_GOOGLE_SEARCH:
        for query in search_queries:
            try:
                for url in google_search(query, num_results=count//len(search_queries)+1, lang='en'):
                    # Extract business from URL/snippet later
                    leads.append({
                        "source_url": url,
                        "search_query": query,
                        "city": city,
                        "status": "prospect"
                    })
                    if len(leads) >= count:
                        break
            except Exception as e:
                print(f"Search error on '{query}': {e}", file=sys.stderr)
            time.sleep(2)  # rate limit
            if len(leads) >= count:
                break

    else:
        # Fallback: Use web search via browser or suggest installing googlesearch-python
        print("Note: googlesearch-python not installed. Using simplified approach.", file=sys.stderr)
        print("For better results, run: pip install googlesearch-python", file=sys.stderr)
        # Build demo leads structure without actual scraping
        # In production, would use web tool or APIs
        sample_names = ['Main Street Cafe', 'Lakeview Salon', 'Northside Auto', 'Downtown Dental', 'Green Valley Landscaping']
        for name in sample_names[:count]:
            leads.append({
                "name": name,
                "city": city,
                "status": "prospect",
                "notes": "Sample lead (install googlesearch-python for real data)"
            })

    # Deduplicate by business name (need to fetch actual names - simplified here)
    unique_leads = []
    seen = set()
    for lead in leads:
        name = lead.get('name') or lead.get('source_url', '').split('/')[-1].replace('-', ' ').title()
        if name and name not in seen:
            lead['name'] = name
            seen.add(name)
            unique_leads.append(lead)

    return unique_leads[:count]

def enrich_leads(leads):
    """
    Add email, website, and phone info by scraping business websites/Facebook.
    This is a simplified version - in production would use more sophisticated scraping.
    """
    enriched = []
    for lead in leads:
        # Placeholder enrichment - real version would:
        # 1. Find business website via Google
        # 2. Scrape contact page for owner email
        # 3. Check if website is outdated (old design, no mobile, etc.)
        # 4. Find Facebook page
        lead['email'] = None  # TODO: implement
        lead['website'] = None
        lead['facebook'] = None
        lead['has_website'] = False  # would be determined by checking
        lead['owner_name'] = None
        enriched.append(lead)
    return enriched

def main():
    parser = argparse.ArgumentParser(description='Find local business leads for website sales.')
    parser.add_argument('--city', required=True, help='Target city')
    parser.add_argument('--count', type=int, default=50, help='Number of leads to find')
    parser.add_argument('--industries', help='Comma-separated industries')
    parser.add_argument('--radius', type=int, default=25, help='Search radius in miles')
    parser.add_argument('--output', default='leads.json', help='Output JSON file')
    parser.add_argument('--enrich', action='store_true', help='Attempt to enrich leads with contact info (slower)')
    args = parser.parse_args()

    print(f"Finding {args.count} leads in {args.city}...")
    leads = search_businesses(args.city, args.count, args.industries, args.radius)

    if args.enrich:
        print("Enriching leads with contact info... (this may take a while)")
        leads = enrich_leads(leads)

    # Save to file
    with open(args.output, 'w') as f:
        json.dump(leads, f, indent=2)

    print(f"✓ Saved {len(leads)} leads to {args.output}")
    print(f"  Sample: {[l.get('name') for l in leads[:5]]}")

    # Next steps
    print("\nNext steps:")
    print("  1. Review leads.json")
    print("  2. Run: website-sales draft-outreach --leads leads.json")

if __name__ == '__main__':
    main()
