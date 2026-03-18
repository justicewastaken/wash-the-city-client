---
name: ig-army
description: Instagram content distribution system: monitor a source account, download reels, and auto-post to 50+ satellite accounts with staggered timing and proxy support.
homepage: https://github.com/your-repo/ig-army
---

# IG Army Skill

Distribute Instagram Reels from a source account to multiple satellite accounts automatically.

## Setup

1. **Install dependencies** (already done): `npm ci`
2. **Configure accounts**: Edit `config/accounts.json` (use `config/accounts.example.json` as template)
   - Set source account credentials
   - Add satellite usernames and proxy details
3. **Set environment variables**: Create `.env` file with passwords/secrets
4. **Initial login**: Run health check to trigger login for each account

## Usage

Run orchestrator commands via Node:

```bash
node /root/.openclaw/workspace/skills/ig-army/scripts/orchestrator.js [command]
```

Commands:
- `monitor` - Check source account for new reels, download to content-bank
- `distribute` - Post all undistributed content to satellite accounts (staggered)
- `health` - Check account session health, flag old/failing accounts
- `once` - Full cycle: monitor + distribute
- `daemon` - Run continuously (monitor every 15min, health every 6h)

## OpenClaw Integration

You can trigger these as tasks:

- Full run: `node /root/.openclaw/workspace/skills/ig-army/scripts/orchestrator.js once`
- Distribute only: `node /root/.openclaw/workspace/skills/ig-army/scripts/orchestrator.js distribute`
- Health check: `node /root/.openclaw/workspace/skills/ig-army/scripts/orchestrator.js health`

## Requirements

- Residential proxies for each satellite account (Smartproxy, IPRoyal, Bright Data)
- VPS with 4GB+ RAM recommended for 50+ accounts
- Instagram accounts (source + satellites) with session JSON stored in `sessions/`

## Notes

- Sessions auto-save after logins and posts
- Accounts with 3+ consecutive failures auto-disable
- Distribution staggered: 1-5 min between posts, 10-15 min between batches
- Content manifest in `content-bank/manifest.json` tracks distribution status
