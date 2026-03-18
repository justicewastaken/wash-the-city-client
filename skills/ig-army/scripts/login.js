// Automated login script to create Instagram session files
// Usage: node scripts/login.js <username> <session_file_path>
// Requires username/password in .env or passed as args

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const [username, sessionFile] = process.argv.slice(2);

if (!username || !sessionFile) {
  console.error('Usage: node scripts/login.js <username> <session_file_path>');
  process.exit(1);
}

// Find password from .env or from SAT_XXX_PASS / SOURCE_PASS
function getPassword(username, config) {
  // Check if it's the source account
  if (config.source_account.username === username) {
    return process.env.SOURCE_PASS;
  }
  // Find satellite account by username
  const sat = config.satellite_accounts.find(a => a.username === username);
  if (sat) {
    return process.env[sat.password_env];
  }
  return null;
}

(async () => {
  const configPath = path.resolve(__dirname, '../config/accounts.json');
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const password = getPassword(username, config);

  if (!password) {
    console.error(`Error: No password found for ${username} in .env (expected SOURCE_PASS or SAT_XXX_PASS)`);
    process.exit(1);
  }

  console.log(`[Login] Attempting to log in as ${username}...`);
  console.log('[Login] A browser window will open. Please log in manually, then press ENTER here.');

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    viewport: { width: 1366, height: 768 },
  });

  const page = await context.newPage();
  await page.goto('https://www.instagram.com/accounts/login/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // Fill login form
  await page.fill('input[name="username"]', username);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');

  // Wait for navigation / home feed
  try {
    await page.waitForURL('**/accounts/onetap/**', { timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(2000);
  } catch (e) {
    // Might be challenge or success page
  }

  // Check if login succeeded (look for home feed or avatar)
  const loggedIn = await page.isVisible('nav').catch(() => false);
  if (!loggedIn) {
    console.error('[Login] Failed to confirm login. Possible challenge or incorrect credentials.');
    await page.screenshot({ path: '/tmp/ig-login-fail.png' });
    console.error('Screenshot saved to /tmp/ig-login-fail.png');
    await browser.close();
    process.exit(1);
  }

  // Save session
  const storageState = await context.storageState();
  const fullPath = path.resolve(__dirname, '..', sessionFile);
  fs.writeFileSync(fullPath, JSON.stringify(storageState, null, 2));
  console.log(`[Login] Session saved to ${fullPath}`);

  await browser.close();
  console.log('[Login] Done.');
})().catch(err => {
  console.error('Login failed:', err);
  process.exit(1);
});
