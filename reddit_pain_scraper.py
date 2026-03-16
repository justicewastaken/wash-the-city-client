#!/usr/bin/env python3
"""
Reddit Niche Pain Point Scraper
Scrapes posts from targeted subreddits to identify recurring business problems.
Perfect for finding automation opportunities.

Usage: python3 reddit_pain_scraper.py [subreddit] [days_back]
Example: python3 reddit_pain_scraper.py dentistry 180
"""

import requests
import json
import sys
import time
from datetime import datetime, timedelta
from collections import Counter
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

PAIN_KEYWORDS = {
    'time_management': ['hours', 'week', 'time', 'manual', 'automate', 'automatic', 'waste', 'spending', 'takes'],
    'money_loss': ['losing', 'lost', 'cost', 'expensive', 'fee', 'fine', 'penalty', 'revenue', 'money'],
    'frustration': ['frustrated', 'annoying', 'hate', 'sucks', 'nightmare', 'pain', 'struggle', 'difficult'],
    'scattered': ['everywhere', 'lost', 'disorganized', 'mess', 'chaos', 'hard to find', 'track'],
    'follow_up': ['follow up', 'follow-up', 'chasing', 'reminder', 'forget', 'slipping through'],
    'paperwork': ['forms', 'paperwork', 'documents', 'records', 'files', ' HIPAA', 'consent', 'signature'],
    'appointments': ['no-show', 'no show', 'cancellation', 'late', 'reschedule', 'booking', 'schedule'],
    'insurance': ['insurance', 'claims', 'verification', 'benefits', 'eligibility', 'preauthorization'],
    'communication': ['call', 'email', 'text', 'SMS', 'notification', 'message', 'reminder'],
}

def get_timestamp_days_ago(days):
    return int((datetime.now() - timedelta(days=days)).timestamp())

def scrape_subreddit(subreddit, days_back=180, min_comments=3):
    """Scrape posts from a subreddit within the last N days."""
    print(f"Scraping r/{subreddit} for posts from last {days_back} days...")
    
    after_timestamp = get_timestamp_days_ago(days_back)
    posts = []
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    
    params = {
        'q': '',
        'restrict_sr': 'on',
        'sort': 'new',
        'limit': 100,
        't': 'all'
    }
    
    page_count = 0
    while True:
        try:
            resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
            if resp.status_code != 200:
                print(f"Error: Reddit returned {resp.status_code}")
                break
                
            data = resp.json()
            children = data.get('data', {}).get('children', [])
            
            if not children:
                break
                
            for child in children:
                post = child['data']
                created = post['created_utc']
                
                # Stop if we're past our date range
                if created < after_timestamp:
                    print(f"Reached posts older than {days_back} days. Stopping.")
                    break
                    
                if post['num_comments'] >= min_comments:
                    posts.append({
                        'title': post['title'],
                        'selftext': post.get('selftext', ''),
                        'num_comments': post['num_comments'],
                        'permalink': post['permalink'],
                        'created_utc': created,
                        'subreddit': subreddit
                    })
            
            # Check if we should continue (Reddit's pagination uses 'after')
            after = data['data'].get('after')
            if not after:
                break
            params['after'] = after
            page_count += 1
            
            if page_count >= 10:  # Safety limit
                print("Reached 10 pages (1000 posts). Stopping.")
                break
                
            time.sleep(2)  # Be polite
            
        except Exception as e:
            print(f"Error during scrape: {e}")
            break
    
    print(f"Collected {len(posts)} posts from r/{subreddit}")
    return posts

def extract_pain_points(text):
    """Simple keyword-based pain point detection."""
    text_lower = text.lower()
    matches = []
    
    for category, keywords in PAIN_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                matches.append(category)
                break
    
    return matches

def analyze_posts(posts):
    """Analyze collected posts and cluster by pain points."""
    print("\nAnalyzing posts for pain points...")
    
    pain_counter = Counter()
    pain_examples = {}
    
    for post in posts:
        full_text = post['title'] + " " + post['selftext']
        pains = extract_pain_points(full_text)
        
        if pains:
            for pain in pains:
                pain_counter[pain] += 1
                # Store example (only keep first few for each category)
                if pain not in pain_examples or len(pain_examples[pain]) < 3:
                    if pain not in pain_examples:
                        pain_examples[pain] = []
                    pain_examples[pain].append({
                        'title': post['title'][:100],
                        'comments': post['num_comments'],
                        'permalink': post['permalink']
                    })
    
    return {
        'total_posts': len(posts),
        'pain_distribution': pain_counter.most_common(),
        'pain_examples': pain_examples,
        'raw_posts': posts[:50]  # Keep first 50 raw posts for reference
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 reddit_pain_scraper.py <subreddit> [days_back=180] [min_comments=3]")
        print("Example: python3 reddit_pain_scraper.py dentistry 180 5")
        return
    
    subreddit = sys.argv[1]
    days_back = int(sys.argv[2]) if len(sys.argv) > 2 else 180
    min_comments = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    
    posts = scrape_subreddit(subreddit, days_back, min_comments)
    
    if not posts:
        print("No posts collected. Exiting.")
        return
    
    analysis = analyze_posts(posts)
    
    # Save full results
    filename = f"{subreddit}_reddit_analysis_{datetime.now().strftime('%Y%m%d')}.json"
    with open(filename, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"\nFull results saved to: {filename}")
    
    # Print summary
    print("\n" + "="*60)
    print(f"PAIN CLUSTER REPORT: r/{subreddit}")
    print("="*60)
    print(f"Total posts analyzed: {analysis['total_posts']}")
    print(f"Posts with detected pain points: {sum(analysis['pain_distribution'])}")
    print("\nTop Pain Clusters:")
    print("-"*60)
    
    for pain, count in analysis['pain_distribution'][:10]:
        print(f"\n{pain.upper().replace('_', ' ')}: {count} posts")
        if pain in analysis['pain_examples']:
            for ex in analysis['pain_examples'][pain][:2]:
                print(f"  • \"{ex['title']}...\" ({ex['comments']} comments)")
                print(f"    https://reddit.com{ex['permalink']}")
    
    print("\n" + "="*60)
    print("Next steps:")
    print("1. Review the JSON file for full post details")
    print("2. Manually read top examples to validate clusters")
    print("3. Pick the top 2-3 pain points with clearest automation fit")
    print("4. Build guide targeting that specific pain")

if __name__ == "__main__":
    main()
