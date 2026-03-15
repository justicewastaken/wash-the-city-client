#!/usr/bin/env python3
"""
Security Audit — runs daily at 7 AM CT.
Checks: open ports, gateway auth, localhost binding, SSH config, firewall, exposed services.
Outputs JSON report to /root/.openclaw/workspace/security_audit.json
"""

import json
import os
import subprocess
import socket
from datetime import datetime

def run(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "timeout", 1
    except Exception as e:
        return "", str(e), 1

def check_open_ports():
    """Return list of listening ports with process names."""
    out, err, rc = run("ss -tuln")
    ports = []
    if rc == 0:
        for line in out.splitlines():
            if 'LISTEN' in line:
                parts = line.split()
                if len(parts) >= 5:
                    local = parts[4]
                    try:
                        ip, port = local.rsplit(':', 1)
                        ports.append({'ip': ip, 'port': int(port), 'line': line})
                    except:
                        pass
    return ports

def check_gateway_auth():
    """Check if OpenClaw gateway requires authentication."""
    # Check if gateway is running and if there's a token set
    gateway_status, _, _ = run("openclaw gateway status")
    # Simple heuristic: if gateway.conf contains 'auth' or 'token'
    auth_required = False
    try:
        with open('/root/.openclaw/gateway.conf', 'r') as f:
            config = f.read()
            if 'auth' in config.lower() or 'token' in config.lower():
                auth_required = True
    except:
        pass
    return {'status': 'running' in gateway_status.lower(), 'auth_required': auth_required}

def check_localhost_binding():
    """Check services binding to 0.0.0.0 vs 127.0.0.1."""
    dangerous = []
    for p in check_open_ports():
        if p['ip'] in ('0.0.0.0', '::'):
            dangerous.append({'port': p['port'], 'ip': p['ip']})
    return dangerous

def check_ssh_config():
    """Audit /etc/ssh/sshd_config for common hardening."""
    issues = []
    try:
        with open('/etc/ssh/sshd_config', 'r') as f:
            config = f.read().lower()
        if 'permitrootlogin' in config and 'no' not in config:
            issues.append('PermitRootLogin is not explicitly set to no')
        if 'passwordauthentication' in config and 'no' not in config:
            issues.append('PasswordAuthentication is not explicitly set to no')
        if 'protocol' in config and '2' not in config:
            issues.append('Protocol is not set to 2')
    except Exception as e:
        issues.append(f'Could not read sshd_config: {e}')
    return issues

def check_firewall():
    """Check active firewall rules (iptables/nftables/ufw)."""
    active = []
    # iptables
    out, _, rc = run("iptables -L -n")
    if rc == 0 and 'DROP' in out:
        active.append('iptables')
    # nft
    out, _, rc = run("nft list ruleset")
    if rc == 0:
        active.append('nftables')
    # ufw
    out, _, rc = run("ufw status")
    if rc == 0 and 'active' in out.lower():
        active.append('ufw')
    return active

def check_exposed_services():
    """List services listening on external interfaces."""
    exposed = []
    for p in check_open_ports():
        if p['ip'] in ('0.0.0.0', '::', 'any'):
            exposed.append({'port': p['port'], 'ip': p['ip']})
    return exposed

def main():
    report = {
        'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'open_ports': check_open_ports(),
        'gateway_auth': check_gateway_auth(),
        'localhost_binding_risks': check_localhost_binding(),
        'ssh_issues': check_ssh_config(),
        'firewall_active': check_firewall(),
        'exposed_services': check_exposed_services(),
        'hostname': socket.gethostname()
    }
    # Severity rating
    critical = []
    high = []
    medium = []
    low = []

    if not report['gateway_auth'].get('auth_required'):
        critical.append('OpenClaw gateway lacks authentication')
    if report['ssh_issues']:
        high.append(f"SSH config issues: {', '.join(report['ssh_issues'])}")
    if not report['firewall_active']:
        medium.append('No firewall detected (iptables/nftables/ufw)')
    if report['exposed_services']:
        for svc in report['exposed_services']:
            if svc['port'] in (22, 80, 443):
                continue  # expected
            high.append(f"Exposed service on port {svc['port']} ({svc['ip']})")
    if report['localhost_binding_risks']:
        for risk in report['localhost_binding_risks']:
            if risk['port'] not in (22, 80, 443):
                medium.append(f"Service listening on {risk['ip']}:{risk['port']}")

    report['findings'] = {
        'critical': critical,
        'high': high,
        'medium': medium,
        'low': low
    }

    out_path = '/root/.openclaw/workspace/security_audit.json'
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"Security audit complete. Findings: C={len(critical)} H={len(high)} M={len(medium)} L={len(low)}")
    # Print summary for cron log
    print(json.dumps(report['findings'], indent=2))

if __name__ == '__main__':
    main()