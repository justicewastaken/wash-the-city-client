# Instagram Repost Automation

Automatically scrapes top Explore reels (>100k likes) and reposts them with your fixed caption.

## Requirements

- Node.js 18+
- Instagram account (use a dedicated account, not your main)
- Credentials stored in environment variables or edited into the script

## Installation

npm install

## Configuration

Edit `instagram-repost.js` and set:

```js
const CONFIG = {
  username: process.env.IG_USERNAME || 'your_username',
  password: process.env.IG_PASSWORD || 'your_password',
  caption: `Your fixed caption here`,
  minLikes: 100000,
  maxReposts: 3,
};
```

Or set environment variables:

```bash
export IG_USERNAME=your_username
export IG_PASSWORD=your_password
```

## Running

```bash
node instagram-repost.js
```

First run will open a browser window for login. It will save the session to `instagram_session/` so subsequent runs stay logged in.

## Scheduling (Cron)

To run every 2 hours:

```bash
0 */2 * * * cd /root/.openclaw/workspace/instagram-automation && /usr/bin/node instagram-repost.js >> cron.log 2>&1
```

## Notes

- This uses Puppeteer (headless Chrome) to automate Instagram.
- Instagram may flag or ban accounts for automated reposting. Use at your own risk.
- Rate limiting and delays are built-in to appear more human.
- The script is fragile — Instagram changes their UI often, so expect breakage.

## Troubleshooting

- If login fails repeatedly, delete `instagram_session` folder to force fresh login.
- Check `cron.log` for errors when running via cron.
- If you get 2FA, you'll need to handle it manually once; the session should persist.
