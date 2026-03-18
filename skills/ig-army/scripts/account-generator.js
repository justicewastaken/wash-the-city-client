// scripts/account-generator.js
// Generates account config entries with randomized browser fingerprints
// Usage: node account-generator.js --count 50 --prefix niche

const fs = require('fs');
const path = require('path');

const CONFIG_PATH = path.resolve(__dirname, '../config/accounts.json');

// Realistic user agent pool (Chrome on Windows/Mac)
const USER_AGENTS = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
];

const VIEWPORTS = [
  { width: 1920, height: 1080 },
  { width: 1366, height: 768 },
  { width: 1536, height: 864 },
  { width: 1440, height: 900 },
  { width: 1280, height: 720 },
  { width: 1600, height: 900 },
  { width: 1280, height: 800 },
];

const TIMEZONES = [
  'America/New_York',
  'America/Chicago',
  'America/Denver',
  'America/Los_Angeles',
  'America/Phoenix',
  'America/Detroit',
  'America/Indiana/Indianapolis',
];

const LOCALES = ['en-US'];

function randomChoice(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function generateAccounts(count, prefix) {
  const accounts = [];

  for (let i = 1; i <= count; i++) {
    const paddedNum = String(i).padStart(3, '0');
    const id = `${prefix}_${paddedNum}`;

    accounts.push({
      id,
      username: `REPLACE_WITH_USERNAME_${paddedNum}`,
      password_env: `${prefix.toUpperCase()}_${paddedNum}_PASS`,
      session_file: `../sessions/${id}.json`,
      proxy: {
        server: `http://REPLACE_WITH_PROXY:PORT`,
        username: `REPLACE_PROXY_USER`,
        password_env: `PROXY_${paddedNum}_PASS`,
      },
      fingerprint: {
        user_agent: randomChoice(USER_AGENTS),
        viewport: randomChoice(VIEWPORTS),
        locale: randomChoice(LOCALES),
        timezone: randomChoice(TIMEZONES),
      },
      status: 'inactive', // Start inactive until credentials are added
      last_post: null,
      last_health_check: null,
      consecutive_failures: 0,
      notes: '',
    });
  }

  return accounts;
}

function main() {
  const args = process.argv.slice(2);
  const count = parseInt(args[args.indexOf('--count') + 1]) || 5;
  const prefix = args[args.indexOf('--prefix') + 1] || 'sat';

  console.log(`Generating ${count} account configs with prefix "${prefix}"...`);

  // Load or create config
  let config;
  if (fs.existsSync(CONFIG_PATH)) {
    config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    console.log(`Existing config found with ${config.satellite_accounts.length} accounts`);
  } else {
    config = {
      source_account: {
        username: 'REPLACE_WITH_SOURCE_USERNAME',
        session_file: '../sessions/source.json',
        proxy: null,
        notes: 'Professional account - source of all content',
      },
      satellite_accounts: [],
    };
  }

  const newAccounts = generateAccounts(count, prefix);
  config.satellite_accounts.push(...newAccounts);

  fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
  console.log(`\nAdded ${count} accounts. Total: ${config.satellite_accounts.length}`);
  console.log(`\nNext steps:`);
  console.log(`1. Edit config/accounts.json to fill in real usernames`);
  console.log(`2. Set password env vars (${prefix.toUpperCase()}_001_PASS, etc.) in .env`);
  console.log(`3. Configure proxy details for each account`);
  console.log(`4. Change status from "inactive" to "active" as accounts are ready`);
  console.log(`5. Run: node scripts/health.js to verify all sessions`);

  // Generate .env template
  const envTemplate = newAccounts.map(a =>
    `${a.password_env}=\nPROXY_${a.id.split('_').pop()}_PASS=`
  ).join('\n');

  const envPath = path.resolve(__dirname, '../.env.template');
  fs.writeFileSync(envPath, envTemplate + '\n');
  console.log(`\nEnv template saved to .env.template`);
}

if (require.main === module) {
  main();
}
