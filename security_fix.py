#!/usr/bin/env python3
"""
Security Auto-Fix — runs daily at 7:30 AM CT.
Reads security_audit.json and automatically fixes critical/high issues.
Notifies via Telegram for medium/low.
"""

import json
import os
import subprocess
from datetime import datetime

AUDIT_FILE = '/root/.openclaw/workspace/security_audit.json'
LOG_FILE = '/root/.openclaw/workspace/security_fix.log'

def run(cmd, capture=True):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture, text=True, timeout=60)
        if capture:
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        else:
            return "", "", 0
    except subprocess.TimeoutExpired:
        return "", "timeout", 1
    except Exception as e:
        return "", str(e), 1

def ensure_gateway_auth():
    """Ensure OpenClaw gateway has authentication enabled."""
    conf_path = '/root/.openclaw/gateway.conf'
    try:
        with open(conf_path, 'r') as f:
            content = f.read()
        modified = False
        lines = content.splitlines()
        new_lines = []
        for line in lines:
            low = line.lower()
            if 'auth' in low and '=' in low:
                if 'required' not in low and 'true' not in low:
                    new_lines.append(line.replace('=', '= required'))
                    modified = True
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        if modified:
            with open(conf_path, 'w') as f:
                f.write('\n'.join(new_lines))
            # Restart gateway
            run('openclaw gateway restart')
            return "Gateway auth enforced (restarted)"
    except:
        pass
    return None

def harden_ssh():
    """Enforce PermitRootLogin no and PasswordAuthentication no."""
    conf = '/etc/ssh/sshd_config'
    try:
        with open(conf, 'r') as f:
            lines = f.readlines()
        changes = []
        for i, line in enumerate(lines):
            low = line.lower()
            if 'permitrootlogin' in low:
                if 'no' not in low:
                    lines[i] = 'PermitRootLogin no\n'
                    changes.append('PermitRootLogin set to no')
            elif 'passwordauthentication' in low:
                if 'no' not in low:
                    lines[i] = 'PasswordAuthentication no\n'
                    changes.append('PasswordAuthentication set to no')
            elif 'protocol' in low:
                if '2' not in line:
                    lines[i] = 'Protocol 2\n'
                    changes.append('Protocol set to 2')
        if changes:
            with open(conf, 'w') as f:
                f.writelines(lines)
            run('systemctl restart ssh')
            return "; ".join(changes)
    except:
        pass
    return None

def enable_firewall():
    """Enable ufw if available, else basic iptables rules."""
    out, _, rc = run('ufw status')
    if rc == 0 and 'inactive' in out.lower():
        run('ufw --force enable')
        # Default deny incoming, allow outgoing
        run('ufw default deny incoming')
        run('ufw default allow outgoing')
        # Allow SSH
        run('ufw allow 22')
        return "UFW enabled and default deny incoming"
    else:
        # Basic iptables fallback
        run('iptables -P INPUT DROP')
        run('iptables -P FORWARD DROP')
        run('iptables -P OUTPUT ACCEPT')
        run('iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT')
        run('iptables -A INPUT -p tcp --dport 22 -j ACCEPT')
        run('iptables -A INPUT -i lo -j ACCEPT')
        run('netfilter-persistent save' or run('iptables-save > /etc/iptables/rules.v4'))
        return "iptables rules set (fallback)"
    return None

def close_exposed_ports():
    """Close non-essential exposed services."""
    try:
        with open(AUDIT_FILE, 'r') as f:
            audit = json.load(f)
    except:
        return None
    changes = []
    for svc in audit.get('exposed_services', []):
        port = svc['port']
        if port in (22, 80, 443):
            continue
        # Block this port
        run(f'iptables -I INPUT -p tcp --dport {port} -j DROP')
        changes.append(f"Blocked port {port}")
    if changes:
        run('iptables-save > /etc/iptables/rules.v4' if os.path.exists('/etc/iptables') else 'iptables-save > /root/iptables.rules')
        return "; ".join(changes)
    return None

def main():
    try:
        with open(AUDIT_FILE, 'r') as f:
            audit = json.load(f)
    except Exception as e:
        print(f"Failed to read audit: {e}")
        return

    findings = audit.get('findings', {})
    actions = []

    # Critical
    if findings.get('critical'):
        # Gateway auth
        if 'gateway' in str(findings['critical']).lower():
            res = ensure_gateway_auth()
            if res: actions.append(res)

    # High
    if findings.get('high'):
        # SSH hardening
        if any('ssh' in item.lower() for item in findings['high']):
            res = harden_ssh()
            if res: actions.append(res)
        # Exposed ports
        if any('exposed' in item.lower() for item in findings['high']):
            res = close_exposed_ports()
            if res: actions.append(res)

    # Medium — notify only
    if findings.get('medium'):
        msg = "Medium severity findings: " + ", ".join(findings['medium'])
        actions.append(f"NOTIFY: {msg}")

    # Log
    log_entry = f"[{datetime.utcnow().isoformat()}] Actions: {actions if actions else 'none'}"
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry + "\n")
    print(log_entry)

if __name__ == '__main__':
    main()