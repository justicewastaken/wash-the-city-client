// scripts/health.js
// Checks the health of all satellite accounts
// Verifies sessions are valid, flags issues, generates status report

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const CONFIG_PATH = path.resolve(__dirname, '../config/accounts.json');
const LOG_DIR = path.resolve(__dirname, '../logs');

class HealthChecker {
  constructor() {
    this.config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  }

  async checkAllAccounts() {
    const accounts = this.config.satellite_accounts;
    console.log(`[Health] Checking ${accounts.length} accounts...\n`);

    const results = [];

    for (const account of accounts) {
      const result = await this.checkAccount(account);
      results.push(result);

      // Brief delay between checks
      await new Promise(r => setTimeout(r, 2000 + Math.random() * 3000));
    }

    // Update config with health check results
    for (const result of results) {
      const account = this.config.satellite_accounts.find(a => a.id === result.id);
      if (account) {
        account.last_health_check = result.checked_at;
        if (result.status === 'session_expired' || result.status === 'login_challenge') {
          account.status = 'needs_review';
        }
      }
    }
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(this.config, null, 2));

    // Print summary
    this.printReport(results);

    // Save report
    this.saveReport(results);

    return results;
  }

  async checkAccount(account) {
    console.log(`[Health] Checking ${account.id} (${account.username})...`);

    const result = {
      id: account.id,
      username: account.username,
      checked_at: new Date().toISOString(),
      status: 'unknown',
      session_valid: false,
      can_post: false,
      last_post: account.last_post || 'never',
      issues: [],
    };

    // Check if session file exists
    const sessionPath = path.resolve(__dirname, '..', account.session_file);
    if (!fs.existsSync(sessionPath)) {
      result.status = 'no_session';
      result.issues.push('No session file found - needs initial login');
      console.log(`  -> NO SESSION`);
      return result;
    }

    // Check session file age
    const sessionStat = fs.statSync(sessionPath);
    const ageHours = (Date.now() - sessionStat.mtimeMs) / (1000 * 60 * 60);
    if (ageHours > 168) { // older than 7 days
      result.issues.push(`Session file is ${Math.floor(ageHours / 24)} days old`);
    }

    // Try loading the session in a browser
    let browser;
    try {
      const launchOptions = { headless: true };
      if (account.proxy) {
        launchOptions.proxy = {
          server: account.proxy.server,
          username: account.proxy.username,
          password: process.env[account.proxy.password_env] || '',
        };
      }

      browser = await chromium.launch(launchOptions);

      const storageState = JSON.parse(fs.readFileSync(sessionPath, 'utf8'));
      const context = await browser.newContext({
        storageState,
        userAgent: account.fingerprint?.user_agent,
        viewport: account.fingerprint?.viewport || { width: 1366, height: 768 },
      });

      const page = await context.newPage();
      await page.goto('https://www.instagram.com/', { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(3000);

      // Check if we're logged in
      const newPostBtn = await page.$('[aria-label="New post"], svg[aria-label="New post"]');
      const loginForm = await page.$('input[name="username"]');
      const challengeForm = await page.$('input[name="verificationCode"], [id*="challenge"]');

      if (newPostBtn) {
        result.session_valid = true;
        result.can_post = true;
        result.status = 'healthy';
        console.log(`  -> HEALTHY`);
      } else if (challengeForm) {
        result.status = 'login_challenge';
        result.issues.push('Account is facing a login challenge (verification required)');
        console.log(`  -> CHALLENGE`);
      } else if (loginForm) {
        result.status = 'session_expired';
        result.issues.push('Session has expired, needs re-login');
        console.log(`  -> EXPIRED`);
      } else {
        result.status = 'unknown';
        result.issues.push('Could not determine login state');
        console.log(`  -> UNKNOWN`);
      }

      // If logged in, check for any action blocks or restrictions
      if (result.session_valid) {
        try {
          await page.goto(`https://www.instagram.com/${account.username}/`, {
            waitUntil: 'networkidle',
            timeout: 15000,
          });
          await page.waitForTimeout(2000);

          const errorPage = await page.$('h2:has-text("Sorry")');
          if (errorPage) {
            result.issues.push('Profile page shows error - possible restriction');
            result.status = 'restricted';
            result.can_post = false;
          }
        } catch (e) {
          result.issues.push(`Could not load profile: ${e.message}`);
        }
      }
    } catch (e) {
      result.status = 'error';
      result.issues.push(`Health check error: ${e.message}`);
      console.log(`  -> ERROR: ${e.message}`);
    } finally {
      if (browser) await browser.close();
    }

    return result;
  }

  printReport(results) {
    console.log(`\n${'='.repeat(70)}`);
    console.log('ACCOUNT HEALTH REPORT');
    console.log(`${'='.repeat(70)}`);

    const statusCounts = {};
    for (const r of results) {
      statusCounts[r.status] = (statusCounts[r.status] || 0) + 1;
    }

    console.log('\nSummary:');
    Object.entries(statusCounts).forEach(([status, count]) => {
      const icon = status === 'healthy' ? '✅' : status === 'error' ? '❌' : '⚠️';
      console.log(`  ${icon} ${status}: ${count}`);
    });

    console.log('\nDetails:');
    console.log(`${'─'.repeat(70)}`);

    for (const r of results) {
      const statusIcon = r.status === 'healthy' ? '✅' : r.status === 'error' ? '❌' : '⚠️';
      console.log(`  ${statusIcon} ${r.id.padEnd(12)} ${r.username.padEnd(25)} ${r.status}`);
      if (r.issues.length > 0) {
        r.issues.forEach(issue => console.log(`     └─ ${issue}`));
      }
    }

    console.log(`\n${'='.repeat(70)}`);
  }

  saveReport(results) {
    if (!fs.existsSync(LOG_DIR)) {
      fs.mkdirSync(LOG_DIR, { recursive: true });
    }

    const reportFile = path.join(LOG_DIR, `health_${new Date().toISOString().split('T')[0]}.json`);
    fs.writeFileSync(reportFile, JSON.stringify({
      checked_at: new Date().toISOString(),
      total_accounts: results.length,
      healthy: results.filter(r => r.status === 'healthy').length,
      issues: results.filter(r => r.status !== 'healthy').length,
      results,
    }, null, 2));
    console.log(`Report saved to ${reportFile}`);
  }
}

async function main() {
  const checker = new HealthChecker();
  await checker.checkAllAccounts();
}

module.exports = { HealthChecker };

if (require.main === module) {
  main();
}
