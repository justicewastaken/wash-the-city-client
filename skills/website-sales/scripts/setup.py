#!/usr/bin/env python3
"""
Setup script for website-sales skill.
Run once to configure environment and validate dependencies.
"""

import os
import json
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
REFERENCES_DIR = SKILL_DIR / 'references'

def print_step(title):
    print(f"\n{'='*50}\n{title}\n{'='*50}")

def check_dependency(cmd, install_suggestion=None):
    """Check if a command exists."""
    try:
        subprocess.run([cmd, '--version'], capture_output=True, check=False, timeout=5)
        print(f"  ✓ {cmd} is installed")
        return True
    except FileNotFoundError:
        print(f"  ✗ {cmd} not found")
        if install_suggestion:
            print(f"    → {install_suggestion}")
        return False

def main():
    print_step("Website Sales Skill Setup")

    # 1. Check gog
    print_step("1. Checking gog (Gmail/Calendar)")
    if check_dependency('gog', 'Install: brew install steipete/tap/gogcli'):
        print("    gog should be authenticated. Test with: gog gmail search --max 1")
    else:
        print("    Please install gog and authenticate before continuing.")
        print("    https://github.com/steipete/gogcli")

    # 2. Check Python deps
    print_step("2. Checking Python dependencies")
    deps = {
        'googlesearch-python': 'pip install googlesearch-python',
        'requests': 'pip install requests'
    }
    for pkg, install in deps.items():
        try:
            __import__(pkg.replace('-', '_'))
            print(f"  ✓ {pkg}")
        except ImportError:
            print(f"  ✗ {pkg} not installed")
            print(f"    → {install}")

    # 3. Check environment
    print_step("3. Environment configuration")
    gog_password = os.environ.get('GOG_KEYRING_PASSWORD')
    whop_key = os.environ.get('WHOP_API_KEY')
    portfolio = os.environ.get('PORTFOLIO_URL')
    phone = os.environ.get('YOUR_PHONE')

    print(f"  GOG_KEYRING_PASSWORD: {'✓ Set' if gog_password else '✗ Not set (set before sending emails)'}")
    print(f"  WHOP_API_KEY: {'✓ Set' if whop_key else '✗ Not set (set before generating payment links)'}")
    print(f"  PORTFOLIO_URL: {portfolio if portfolio else '✗ Not set (highly recommended)'}")
    print(f"  YOUR_PHONE: {phone if phone else '✗ Not set (highly recommended)'}")

    # 4. Check config files
    print_step("4. Configuration files")
    whop_config = REFERENCES_DIR / 'whop-config.json'
    if whop_config.exists():
        with open(whop_config) as f:
            cfg = json.load(f)
            product_id = cfg.get('product_id')
            print(f"  ✓ whop-config.json found")
            print(f"    Product ID: {product_id if product_id and product_id != 'your_whop_product_id_here' else '⚠️  Needs your product ID'}")
    else:
        print(f"  ✗ whop-config.json not found")
        print(f"    → Copy template: cp {REFERENCES_DIR / 'whop-config-template.json'} {whop_config}")
        print(f"    → Then edit with your Whop product ID and prices")

    # 5. Make scripts executable
    print_step("5. Making scripts executable")
    scripts_dir = SKILL_DIR / 'scripts'
    for script in scripts_dir.glob('*.py'):
        script.chmod(0o755)
        print(f"  ✓ {script.name}")

    # 6. Test commands
    print_step("6. Testing commands")
    website_sales = SKILL_DIR / 'website-sales'
    try:
        result = subprocess.run([str(website_sales), 'find-leads', '--help'], capture_output=True, timeout=5)
        print("  ✓ website-sales CLI working")
    except Exception as e:
        print(f"  ✗ Error testing CLI: {e}")

    # 7. Next steps
    print_step("Setup Complete! Next Steps:")
    print("""
1. Create Whop product and get product ID
   → Edit references/whop-config.json
2. Set environment variables:
   export WHOP_API_KEY="your_key"
   export PORTFOLIO_URL="https://yourportfolio.com"
   export YOUR_PHONE="555-555-5555"
   export GOG_KEYRING_PASSWORD="your_gog_password"
3. Test with a small batch:
   website-sales find-leads --city "Eau Claire" --count 10 --output leads.json
   (Manually add emails to leads.json or integrate email finder)
   website-sales draft-outreach --leads leads.json --output emails.json
   website-sales send-emails --emails emails.json --leads leads.json --dry-run
4. Once happy, send real emails:
   website-sales send-emails --emails emails.json --leads leads.json --batch-size 25
5. Track responses: website-sales track-leads --lead-id "business-name" --status responded
6. Generate payment links: website-sales generate-payment --lead "Business" --email "owner@example.com"

Read references/SETUP.md for detailed guidance.
""")

    print_step("All Done!")
    print("The 'website-sales' command is ready. Run it from anywhere in your workspace.")

if __name__ == '__main__':
    main()
