# Google Integrations — Quick Reference

## Gmail & Calendar Access (gog CLI)

**Service Account Credentials:**
- Path: `/root/.openclaw/workspace/.config/gog/client_secret.json`
- Account: `justiceforanything@gmail.com`
- This service account has been granted access to the primary Google Calendar

**Problem:** The keyring is locked, causing `gog` commands to hang waiting for a passphrase.

**Solutions:**

### Option 1: Set Keyring Password in Environment (Quick Fix)
Set `GOG_KEYRING_PASSWORD` in the environment:
```bash
export GOG_KEYRING_PASSWORD="opensesame"
```
Add to shell profile or OpenClaw config for persistence.

### Option 2: Use App Password (Recommended)
1. Enable 2FA on Google Account
2. Generate app password for "Mail"
3. Reconfigure `gog` to use SMTP with the app password (bypasses OAuth/keyring)

### Option 3: Unlock Keyring Once Per Session
Manually unlock the keyring by providing the passphrase when prompted.

---

**Usage once unlocked:**
```bash
# List upcoming events
gog calendar list --calendar primary --days 7

# Create event
gog calendar create primary \
  --summary "Event Title" \
  --from "2026-03-18T09:00:00-05:00" \
  --to "2026-03-18T10:00:00-05:00" \
  --description "Details here"
```

---

*Last updated: 2026-03-18*
