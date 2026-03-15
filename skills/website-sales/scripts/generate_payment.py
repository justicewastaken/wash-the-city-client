#!/usr/bin/env python3
"""
Generate Whop payment links for leads.
"""

import argparse
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime

def get_whop_product_id():
    """Get Whop product ID from config or env."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'references', 'whop-config.json')
    if os.path.exists(config_path):
        with open(config_path) as f:
            cfg = json.load(f)
            return cfg.get('product_id')
    return os.environ.get('WHOP_PRODUCT_ID')

def create_whop_link(customer_email, business_name, package_type='setup+monthly', api_key=None):
    """
    Create a unique Whop payment link.
    Uses whop CLI if available, or API directly.
    """
    # Try using whop CLI first
    try:
        # Check if whop CLI is installed
        subprocess.run(['whop', '--version'], capture_output=True, check=False, timeout=5)
        # Use whop CLI to create link
        product_id = get_whop_product_id()
        if not product_id:
            return None, "Whop product ID not configured"

        cmd = [
            'whop', 'products', 'purchase-link', 'create',
            '--product', product_id,
            '--email', customer_email,
            '--metadata', f"business={business_name},type={package_type},generated={datetime.now().isoformat()}"
        ]
        if api_key:
            cmd.extend(['--api-key', api_key])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            link_data = json.loads(result.stdout)
            return link_data.get('url'), None
        else:
            return None, result.stderr
    except FileNotFoundError:
        # Fall back to direct API call
        return create_whop_link_api(customer_email, business_name, package_type, api_key)
    except Exception as e:
        return None, str(e)

def create_whop_link_api(customer_email, business_name, package_type, api_key):
    """Direct API call to Whop (requires requests)."""
    try:
        import requests
    except ImportError:
        return None, "Whop CLI not installed and requests library not available"

    product_id = get_whop_product_id()
    if not product_id:
        return None, "Whop product ID not configured"

    url = f"https://api.whop.com/api/v2/products/{product_id}/purchase-links"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "email": customer_email,
        "metadata": {
            "business": business_name,
            "type": package_type,
            "generated": datetime.now().isoformat()
        }
    }

    try:
        resp = requests.post(url, json=data, headers=headers, timeout=30)
        if resp.status_code in (200, 201):
            link_data = resp.json()
            return link_data.get('url'), None
        else:
            return None, f"API error {resp.status_code}: {resp.text}"
    except Exception as e:
        return None, str(e)

def main():
    parser = argparse.ArgumentParser(description='Generate Whop payment link for a lead.')
    parser.add_argument('--lead', required=True, help='Business name')
    parser.add_argument('--email', required=True, help='Customer email')
    parser.add_argument('--type', default='setup+monthly', choices=['setup-only', 'monthly', 'setup+monthly'], help='Package type')
    parser.add_argument('--whop-api-key', help='Whop API key (or set WHOP_API_KEY env var)')
    parser.add_argument('--output', help='Optional output file to append link')
    args = parser.parse_args()

    api_key = args.whop_api_key or os.environ.get('WHOP_API_KEY')
    if not api_key:
        print("Error: Whop API key required. Set WHOP_API_KEY or use --whop-api-key", file=sys.stderr)
        sys.exit(1)

    print(f"Creating {args.type} payment link for {args.lead} ({args.email})...")
    link, error = create_whop_link(args.email, args.lead, args.type, api_key)

    if error:
        print(f"Failed to create payment link: {error}", file=sys.stderr)
        sys.exit(1)

    print(f"✓ Payment link: {link}")

    # Record the payment link
    record = {
        "business": args.lead,
        "email": args.email,
        "package_type": args.type,
        "payment_link": link,
        "created": datetime.now().isoformat()
    }

    if args.output:
        try:
            # Append to JSON lines file
            with open(args.output, 'a') as f:
                f.write(json.dumps(record) + '\n')
            print(f"  Record saved to {args.output}")
        except Exception as e:
            print(f"  Warning: could not save to {args.output}: {e}", file=sys.stderr)

    print("\nNext:")
    print("  1. Include this link in your follow-up email")
    print("  2. Track payment status in Whop dashboard")
    print("  3. Once paid, update lead status: website-sales track-leads --lead-id ... --status paid")

if __name__ == '__main__':
    main()
