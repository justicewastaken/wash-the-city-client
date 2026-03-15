#!/usr/bin/env python3
"""
Cron Health Monitor — runs daily at 9 AM CT.
Checks all cron jobs, verifies they ran successfully, flags failures or missing entries.
Can self-heal by re-adding known jobs from a registry.
"""

import json
import os
import subprocess
import re
from datetime import datetime, timedelta

WORKSPACE = '/root/.openclaw/workspace'
REGISTRY_PATH = os.path.join(WORKSPACE, 'cron_registry.json')
STATUS_PATH = os.path.join(WORKSPACE, 'cron_status.json')
LOG_PATTERNS = {
    'pipeline_backup': 'backup.log',
    'security_audit': 'security_audit.log',
    'security_fix': 'security_fix.log',
    'api_health': 'api_health.log',
    'pipeline_summary': 'pipeline_summary.log',
    'improver': 'improver.log',
    'website_sales': 'pipeline_send_*.log',
    'recursive_improver': 'improver.log'
}
CRON_TIMES = {
    'backup_workspace.sh': '0 */2 * * *',
    'security_audit.py': '0 13 * * *',
    'security_fix.py': '30 13 * * *',
    'api_health_check.py': '0 14 * * *',
    'morning_briefing.sh': '0 14 * * *',  # placeholder; adjust as needed
    'daily_website_batch.py (multiple)': '0 12,13,14,15,16 * * *',
    'recursive_improver.py': '0 7,19 * * *',
    'website-sales-pipeline (scrape)': '0 8 * * *'
}

def log(msg):
    ts = datetime.utcnow().isoformat() + 'Z'
    print(f"[{ts}] {msg}")
    with open(os.path.join(WORKSPACE, 'cron_health.log'), 'a') as f:
        f.write(f"[{ts}] {msg}\n")

def run(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def get_current_crontab():
    out, err, rc = run('crontab -l')
    if rc != 0:
        return []
    return out.splitlines()

def load_registry():
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH) as f:
            return json.load(f)
    # Build registry from known jobs
    registry = {}
    for job, schedule in CRON_TIMES.items():
        registry[job] = {'schedule': schedule, 'command': None, 'status': 'unknown'}
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry, f, indent=2)
    return registry

def save_registry(registry):
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry, f, indent=2)

def check_log_success(pattern, hours_back=48):
    """Check if a pattern-matched log file has recent success."""
    # Find matching log files
    out, _, _ = run(f'find {WORKSPACE} -name "{pattern}" -mmin -{hours_back*60} 2>/dev/null')
    files = out.splitlines()
    if not files:
        return None, "no recent log file"
    # Check last line for success indicators
    for logfile in files:
        try:
            with open(logfile, 'r') as f:
                lines = f.read().splitlines()
            for line in reversed(lines[-50:]):  # check recent lines
                if 'complete' in line.lower() or 'success' in line.lower() or 'sent:' in line.lower():
                    return True, line
        except:
            pass
    return False, "no success marker found"

def verify_cron_presence(registry_keys, crontab_lines):
    """Check each registered job is in the current crontab."""
    missing = []
    for key in registry_keys:
        found = False
        for line in crontab_lines:
            if key in line:
                found = True
                break
        if not found:
            missing.append(key)
    return missing

def self_heal_missing(missing_jobs, crontab_lines, registry):
    """Re-add missing cron entries using registry schedule."""
    added = []
    for job in missing_jobs:
        entry = registry[job]
        if entry.get('command'):
            # Not yet implemented: we'd need to reconstruct command from job name
            pass
        else:
            # For known jobs, map to actual command
            if job == 'backup_workspace.sh':
                cmd = f'0 */2 * * * {WORKSPACE}/backup_workspace.sh >> {WORKSPACE}/backup.log 2>&1'
            elif job == 'security_audit.py':
                cmd = f'0 13 * * * {WORKSPACE}/security_audit.py >> {WORKSPACE}/security_audit.log 2>&1'
            elif job == 'security_fix.py':
                cmd = f'30 13 * * * {WORKSPACE}/security_fix.py >> {WORKSPACE}/security_fix.log 2>&1'
            elif job == 'api_health_check.py':
                cmd = f'0 14 * * * {WORKSPACE}/api_health_check.py >> {WORKSPACE}/api_health.log 2>&1'
            elif job == 'recursive_improver.py':
                cmd = f'0 7,19 * * * {WORKSPACE}/recursive_improver.py >> {WORKSPACE}/improver.log 2>&1'
            elif 'daily_website_batch' in job:
                cmd = f'0 12,13,14,15,16 * * * {WORKSPACE}/daily_website_batch.py --batch-size 10 --send >> {WORKSPACE}/pipeline_send.log 2>&1'
            else:
                continue
            # Add to crontab
            run(f'(crontab -l; echo "{cmd}") | crontab -')
            added.append(job)
    return added

def main():
    log("Cron Health Monitor started")
    crontab_lines = get_current_crontab()
    registry = load_registry()
    status = {}
    alerts = []

    # 1. Presence check
    missing = verify_cron_presence(list(registry.keys()), crontab_lines)
    if missing:
        alerts.append(f"Missing cron entries: {missing}")
        # Attempt self-heal
        added = self_heal_missing(missing, crontab_lines, registry)
        if added:
            alerts.append(f"Re-added: {added}")
            status['healed'] = True
        else:
            status['healed'] = False

    # 2. Log success check per job
    for job in registry.keys():
        pattern = LOG_PATTERNS.get(job, f'{job}.log')
        success, msg = check_log_success(pattern)
        status[job] = {'success': success, 'reason': msg}
        if success is False:
            alerts.append(f"{job} failed/missing: {msg}")

    # 3. Summary
    total = len(registry)
    healthy = sum(1 for v in status.values() if v.get('success'))
    status['summary'] = {'total': total, 'healthy': healthy, 'alerts': len(alerts)}

    # Save status
    with open(STATUS_PATH, 'w') as f:
        json.dump({'timestamp': datetime.utcnow().isoformat()+'Z', 'status': status, 'alerts': alerts}, f, indent=2)

    # Notify if any alerts
    if alerts:
        body = "Cron Health Monitor detected issues:\n\n" + "\n".join(f"- {a}" for a in alerts)
        body += f"\nFull status: {STATUS_PATH}\n"
        # send_alert via gog (skipped for now; could add later)
        log(f"Alerts triggered: {len(alerts)}")
    else:
        log("All cron jobs healthy")

    log(f"Cron health check complete: {healthy}/{total} jobs OK")

if __name__ == '__main__':
    main()