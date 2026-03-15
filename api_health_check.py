#!/usr/bin/env python3
"""
API Health Check — runs daily at 8 AM CT.
Verifies API keys, checks usage against limits, flags anomalies.
Sends email alert for critical/high issues.
"""

import json
import os
import subprocess
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from collections import defaultdict

WORKSPACE = '/root/.openclaw/workspace'
CONFIG_PATH = os.path.join(WORKSPACE, 'api_health_config.json')
HISTORY_PATH = os.path.join(WORKSPACE, 'api_health_history.json')
REPORT_PATH = os.path.join(WORKSPACE, 'api_health_report.json')
LOG_PATH = os.path.join(WORKSPACE, 'api_health.log')

def log(msg):
    ts = datetime.utcnow().isoformat() + 'Z'
    print(f"[{ts}] {msg}")
    with open(LOG_PATH, 'a') as f:
        f.write(f"[{ts}] {msg}\n")

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    # Auto-discover and create default config
    config = {"providers": []}
    # GitHub token
    gh_token_file = os.path.join(WORKSPACE, '.github-token.json')
    if os.path.exists(gh_token_file):
        try:
            with open(gh_token_file) as f:
                data = json.load(f)
                token = data.get('github_token')
                if token:
                    config['providers'].append({
                        "name": "GitHub",
                        "type": "github",
                        "key": token,
                        "monthly_limit": 5000 * 24 * 30,  # approximate requests/month
                        "unit": "requests/month"
                    })
        except:
            pass
    # OpenRouter from env
    or_key = os.environ.get('OPENROUTER_API_KEY')
    if or_key:
        config['providers'].append({
            "name": "OpenRouter",
            "type": "openrouter",
            "key": or_key,
            "monthly_limit": 100,  # default; adjust as needed
            "unit": "credits"
        })
    # Save config for editing
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    log(f"Created config with discovered keys: {[p['name'] for p in config['providers']]}")
    return config

def load_history():
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH) as f:
            return json.load(f)
    return {}

def save_history(history):
    with open(HISTORY_PATH, 'w') as f:
        json.dump(history, f, indent=2)

def check_github(key):
    url = 'https://api.github.com/rate_limit'
    headers = {'Authorization': f'token {key}'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
            core = data.get('resources', {}).get('core', {})
            limit = core.get('limit', 0)
            remaining = core.get('remaining', 0)
            return {'valid': True, 'remaining': remaining, 'limit': limit}
    except Exception as e:
        return {'valid': False, 'error': str(e)}

def check_openrouter(key):
    url = 'https://openrouter.ai/api/v1/account'
    headers = {'Authorization': f'Bearer {key}'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.getcode() != 200:
                return {'valid': False, 'error': f'HTTP {resp.getcode()}'}
            data = json.load(resp)
            # Expected: {"data":{"credits": 85.0, ...}}
            credits = data.get('data', {}).get('credits')
            if credits is not None:
                return {'valid': True, 'remaining': float(credits)}
            else:
                return {'valid': True, 'remaining': None}
    except Exception as e:
        return {'valid': False, 'error': str(e)}

def send_alert(subject, body):
    # Use gog to send email
    env = os.environ.copy()
    env['GOG_KEYRING_PASSWORD'] = env.get('GOG_KEYRING_PASSWORD', 'opensesame')
    cmd = [
        'gog', 'gmail', 'send',
        '--account', 'justiceforanything@gmail.com',
        '--to', 'justiceforanything@gmail.com',
        '--subject', subject,
        '--body', body
    ]
    try:
        subprocess.run(cmd, env=env, timeout=30)
        log("Alert email sent")
    except Exception as e:
        log(f"Failed to send alert: {e}")

def main():
    config = load_config()
    history = load_history()
    today = datetime.utcnow().strftime('%Y-%m-%d')
    report = {'date': today, 'providers': {}, 'alerts': []}

    # Ensure today's entry exists in history
    if today not in history:
        history[today] = {}

    for p in config['providers']:
        name = p['name']
        p_type = p['type']
        key = p.get('key')
        if not key:
            # Try to fetch from env or file dynamically
            if p.get('key_env'):
                key = os.getenv(p['key_env'])
            elif p.get('key_file'):
                try:
                    with open(p['key_file']) as f:
                        data = json.load(f)
                        key = data.get(p.get('key_field', 'token'))
                except:
                    pass
        if not key:
            log(f"Skipping {name}: no key found")
            continue

        # Perform check
        if p_type == 'github':
            result = check_github(key)
        elif p_type == 'openrouter':
            result = check_openrouter(key)
        else:
            result = {'valid': False, 'error': 'unknown provider type'}

        # Record in report
        report['providers'][name] = result
        history[today][name] = result

        # Determine alerts based on thresholds
        if not result.get('valid'):
            alert = f"{name} key invalid: {result.get('error')}"
            report['alerts'].append({'level': 'critical', 'msg': alert})
        else:
            # Check usage vs limit
            limit = p.get('monthly_limit')
            remaining = result.get('remaining')
            if limit and remaining is not None:
                used = limit - remaining
                pct_used = used / limit if limit > 0 else 0
                if pct_used > 0.8:
                    alert = f"{name} usage {pct_used:.1%} of limit (used {used:.1f}/{limit})"
                    report['alerts'].append({'level': 'high', 'msg': alert})

    # Save history
    save_history(history)

    # Compare with 7-day average of remaining (simple anomaly detection)
    # Build dates sorted
    dates = sorted(history.keys())
    if len(dates) >= 2:
        for p in config['providers']:
            name = p['name']
            # Gather last 7 days (excluding today if present)
            values = []
            for d in dates[-7:]:
                if d == today:
                    continue
                val = history[d].get(name, {}).get('remaining')
                if val is not None:
                    values.append(val)
            if len(values) >= 3:
                avg = sum(values) / len(values)
                current = report['providers'].get(name, {}).get('remaining')
                if current is not None and avg > 0:
                    drop_pct = (avg - current) / avg
                    if drop_pct > 0.3:  # usage spiked (remaining dropped >30%)
                        alert = f"{name} remaining {current:.1f} vs 7-day avg {avg:.1f} (drop {drop_pct:.1%})"
                        report['alerts'].append({'level': 'high', 'msg': alert})

    # Summary total spend (approx)
    total_usage = 0
    total_limit = 0
    for p in config['providers']:
        name = p['name']
        res = report['providers'].get(name, {})
        if res.get('valid') and p.get('monthly_limit') and res.get('remaining') is not None:
            limit = p['monthly_limit']
            used = limit - res['remaining']
            total_usage += used
            total_limit += limit
    report['total_usage'] = total_usage
    report['total_limit'] = total_limit

    # Write report
    with open(REPORT_PATH, 'w') as f:
        json.dump(report, f, indent=2)

    # Send immediate email if any critical/high alerts
    critical_high = [a for a in report['alerts'] if a['level'] in ('critical', 'high')]
    if critical_high:
        body = "API Health Check detected issues:\n\n"
        for a in critical_high:
            body += f"- [{a['level']}] {a['msg']}\n"
        body += f"\nFull report: {REPORT_PATH}\n"
        send_alert("API Health Alert", body)
        log("Alert triggered, email sent")
    else:
        log("No critical/high issues")

    log(f"API health check complete. Total usage: {total_usage:.1f}/{total_limit:.1f}")

if __name__ == '__main__':
    main()