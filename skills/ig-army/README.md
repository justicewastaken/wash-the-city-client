# IG Army - Instagram Content Distribution System

## Architecture

```
Source Account (Professional)
    │
    ▼
┌─────────────────┐
│  Source Monitor  │  Polls source account for new reels
└────────┬────────┘
         │ Downloads video + caption
         ▼
┌─────────────────┐
│  Content Bank   │  Local storage of videos + manifest.json
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Distributor    │  Posts to all active satellite accounts
│  (Staggered)    │  1-5 min random delays between each
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Satellite Accounts (50+)              │
│  Each with: session, proxy, fingerprint │
└─────────────────────────────────────────┘
```

## Directory Structure

```
ig-army/
├── config/
│   ├── accounts.json          # All account configs (DO NOT COMMIT)
│   └── accounts.example.json  # Template
├── content-bank/
│   ├── manifest.json          # Tracks all content + distribution status
│   └── *.mp4                  # Downloaded reel videos
├── sessions/
│   └── *.json                 # Playwright session/cookie files per account
├── logs/
│   ├── daily_*.jsonl          # Daily distribution logs
│   ├── dist_*.json            # Per-post distribution results
│   └── health_*.json          # Health check reports
├── scripts/
│   ├── orchestrator.js        # Main entry point
│   ├── monitor.js             # Source account watcher
│   ├── poster.js              # Core Playwright posting module
│   ├── distributor.js         # Staggered distribution engine
│   ├── health.js              # Account health checker
│   └── account-generator.js   # Bulk account config generator
├── .env                       # Passwords and secrets (DO NOT COMMIT)
└── package.json
```

## Setup

### 1. Generate account configs
```bash
node scripts/account-generator.js --count 50 --prefix niche
```

### 2. Configure accounts
Edit `config/accounts.json`:
- Set source account username
- Fill in satellite usernames
- Configure proxy details per account

### 3. Set up environment variables
```bash
cp .env.template .env
# Fill in all passwords
```

### 4. Initial login for each account
Run health check to identify which accounts need manual login:
```bash
node scripts/health.js
```

### 5. Run the system

**Single run** (check + distribute):
```bash
node scripts/orchestrator.js once
```

**Daemon mode** (continuous monitoring):
```bash
node scripts/orchestrator.js daemon
```

**Just distribute** existing undistributed content:
```bash
node scripts/orchestrator.js distribute
```

**Health check** only:
```bash
node scripts/orchestrator.js health
```

## OpenClaw Integration

Each script can be triggered as an OpenClaw skill:

- **Monitor skill**: `node /path/to/ig-army/scripts/orchestrator.js monitor`
- **Distribute skill**: `node /path/to/ig-army/scripts/orchestrator.js distribute`
- **Health skill**: `node /path/to/ig-army/scripts/orchestrator.js health`
- **Full run skill**: `node /path/to/ig-army/scripts/orchestrator.js once`

## Important Notes

### Proxy Requirements
Each satellite account MUST have its own sticky residential proxy. Recommended providers:
- Smartproxy (residential rotating with sticky sessions)
- IPRoyal (static residential)
- Bright Data (premium, more expensive)

Budget: ~$1-3/account/month for residential proxies

### Rate Limiting
- Posts are staggered 1-5 minutes apart per account
- 10-account batches with 10-minute breaks between batches
- 15-30 minute breaks between distributing different posts
- At 50 accounts, full distribution takes ~2-4 hours

### Session Management
- Sessions are saved after every successful login and post
- Sessions older than 7 days get flagged in health checks
- Accounts with 3+ consecutive failures auto-disable

### VPS Requirements
- Minimum 4GB RAM for 50 accounts (sequential posting)
- Only 1 browser instance runs at a time
- Recommend: DigitalOcean 4GB droplet ($24/mo)
