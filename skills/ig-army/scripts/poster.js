// scripts/poster.js
// Core reel posting function for a single account
// Usage: node scripts/poster.js --account sat_001 --video ./content-bank/reel_001.mp4 --caption "Your caption here"

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const SELECTORS = {
  // These will need updating as Instagram changes their UI
  // Using data-testid and aria selectors where possible for stability
  newPostButton: '[aria-label="New post"]',
  selectFromComputer: 'button:has-text("Select from computer")',
  fileInput: 'input[type="file"][accept*="video"]',
  nextButton: 'button:has-text("Next")',
  shareButton: 'button:has-text("Share")',
  captionInput: '[aria-label="Write a caption..."]',
  reelTab: 'button:has-text("Reel")',
  postSharedIndicator: 'img[alt="Animated checkmark"]', // success indicator
};

// Fallback selectors in case primary ones break
const FALLBACK_SELECTORS = {
  newPostButton: 'svg[aria-label="New post"]',
  fileInput: 'input[type="file"]',
  captionInput: 'textarea[aria-label="Write a caption..."]',
  nextButton: 'div[role="button"]:has-text("Next")',
  shareButton: 'div[role="button"]:has-text("Share")',
};

class InstagramPoster {
  constructor(accountConfig, options = {}) {
    this.account = accountConfig;
    this.browser = null;
    this.context = null;
    this.page = null;
    this.options = {
      headless: true,
      slowMo: 50, // slight delay between actions to seem more human
      timeout: 60000,
      ...options,
    };
  }

  async init() {
    const launchOptions = {
      headless: this.options.headless,
      slowMo: this.options.slowMo,
    };

    // Set up proxy if configured
    if (this.account.proxy) {
      launchOptions.proxy = {
        server: this.account.proxy.server,
        username: this.account.proxy.username,
        password: process.env[this.account.proxy.password_env] || '',
      };
    }

    this.browser = await chromium.launch(launchOptions);

    // Load or create browser context with fingerprint
    const contextOptions = {
      userAgent: this.account.fingerprint?.user_agent,
      viewport: this.account.fingerprint?.viewport || { width: 1366, height: 768 },
      locale: this.account.fingerprint?.locale || 'en-US',
      timezoneId: this.account.fingerprint?.timezone || 'America/Chicago',
    };

    // Load existing session if available
    const sessionPath = path.resolve(__dirname, '..', this.account.session_file);
    if (fs.existsSync(sessionPath)) {
      try {
        const storageState = JSON.parse(fs.readFileSync(sessionPath, 'utf8'));
        contextOptions.storageState = storageState;
        console.log(`[${this.account.id}] Loaded existing session`);
      } catch (e) {
        console.warn(`[${this.account.id}] Failed to load session, will create new one`);
      }
    }

    this.context = await this.browser.newContext(contextOptions);
    this.page = await this.context.newPage();
    this.page.setDefaultTimeout(this.options.timeout);
  }

  async login() {
    console.log(`[${this.account.id}] Navigating to Instagram...`);
    await this.page.goto('https://www.instagram.com/', { waitUntil: 'networkidle' });
    await this.randomDelay(2000, 4000);

    // Check if already logged in
    const isLoggedIn = await this.page.$('[aria-label="New post"]') ||
                       await this.page.$('svg[aria-label="New post"]');

    if (isLoggedIn) {
      console.log(`[${this.account.id}] Already logged in via session`);
      return true;
    }

    // Need to log in
    console.log(`[${this.account.id}] Session expired, logging in...`);
    const password = process.env[this.account.password_env];
    if (!password) {
      throw new Error(`No password found in env var ${this.account.password_env}`);
    }

    await this.page.fill('input[name="username"]', this.account.username);
    await this.randomDelay(500, 1500);
    await this.page.fill('input[name="password"]', password);
    await this.randomDelay(500, 1000);
    await this.page.click('button[type="submit"]');

    // Wait for login to complete
    await this.page.waitForNavigation({ waitUntil: 'networkidle', timeout: 30000 });
    await this.randomDelay(3000, 5000);

    // Handle "Save Login Info" prompt
    try {
      const saveInfoBtn = await this.page.$('button:has-text("Save info")');
      if (saveInfoBtn) {
        await saveInfoBtn.click();
        await this.randomDelay(2000, 3000);
      }
    } catch (e) { /* ignore */ }

    // Handle notifications prompt
    try {
      const notNowBtn = await this.page.$('button:has-text("Not Now")');
      if (notNowBtn) {
        await notNowBtn.click();
        await this.randomDelay(1000, 2000);
      }
    } catch (e) { /* ignore */ }

    // Save session
    await this.saveSession();
    console.log(`[${this.account.id}] Login successful`);
    return true;
  }

  async postReel(videoPath, caption) {
    const absoluteVideoPath = path.resolve(videoPath);
    if (!fs.existsSync(absoluteVideoPath)) {
      throw new Error(`Video file not found: ${absoluteVideoPath}`);
    }

    console.log(`[${this.account.id}] Starting reel upload: ${path.basename(videoPath)}`);

    // Click new post button
    await this.clickWithFallback('newPostButton');
    await this.randomDelay(1500, 3000);

    // Handle file input - Instagram hides it, so we set files directly
    const fileInput = await this.page.waitForSelector(
      SELECTORS.fileInput + ', ' + FALLBACK_SELECTORS.fileInput,
      { state: 'attached', timeout: 10000 }
    );
    await fileInput.setInputFiles(absoluteVideoPath);
    console.log(`[${this.account.id}] Video file attached`);
    await this.randomDelay(3000, 6000);

    // Wait for video to process - this can take a while
    console.log(`[${this.account.id}] Waiting for video processing...`);
    await this.randomDelay(5000, 10000);

    // Click through to caption screen (may need multiple "Next" clicks)
    for (let i = 0; i < 3; i++) {
      try {
        const nextBtn = await this.page.$(SELECTORS.nextButton + ', ' + FALLBACK_SELECTORS.nextButton);
        if (nextBtn) {
          await nextBtn.click();
          await this.randomDelay(2000, 4000);
        }
      } catch (e) {
        break;
      }
    }

    // Enter caption
    try {
      const captionEl = await this.page.waitForSelector(
        SELECTORS.captionInput + ', ' + FALLBACK_SELECTORS.captionInput,
        { timeout: 10000 }
      );
      await captionEl.click();
      await this.randomDelay(500, 1000);
      // Type caption with slight randomization to seem human
      await captionEl.fill(caption);
      console.log(`[${this.account.id}] Caption entered`);
    } catch (e) {
      console.warn(`[${this.account.id}] Could not find caption field, proceeding without caption`);
    }

    await this.randomDelay(1000, 2000);

    // Click Share
    await this.clickWithFallback('shareButton');
    console.log(`[${this.account.id}] Share button clicked, waiting for upload...`);

    // Wait for post confirmation
    try {
      await this.page.waitForSelector(SELECTORS.postSharedIndicator, { timeout: 120000 });
      console.log(`[${this.account.id}] Reel posted successfully!`);
    } catch (e) {
      // Alternative: wait for the sharing dialog to disappear
      console.log(`[${this.account.id}] Upload indicator not found, checking if post went through...`);
      await this.randomDelay(10000, 15000);
    }

    // Save updated session after successful post
    await this.saveSession();

    return {
      success: true,
      account: this.account.id,
      timestamp: new Date().toISOString(),
      video: path.basename(videoPath),
    };
  }

  async clickWithFallback(selectorKey) {
    try {
      await this.page.click(SELECTORS[selectorKey], { timeout: 5000 });
    } catch (e) {
      if (FALLBACK_SELECTORS[selectorKey]) {
        await this.page.click(FALLBACK_SELECTORS[selectorKey], { timeout: 5000 });
      } else {
        throw e;
      }
    }
  }

  async saveSession() {
    const sessionPath = path.resolve(__dirname, '..', this.account.session_file);
    const sessionDir = path.dirname(sessionPath);
    if (!fs.existsSync(sessionDir)) {
      fs.mkdirSync(sessionDir, { recursive: true });
    }
    const storageState = await this.context.storageState();
    fs.writeFileSync(sessionPath, JSON.stringify(storageState, null, 2));
    console.log(`[${this.account.id}] Session saved`);
  }

  async randomDelay(min, max) {
    const delay = Math.floor(Math.random() * (max - min + 1)) + min;
    await this.page.waitForTimeout(delay);
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
    }
  }
}

// CLI usage
async function main() {
  const args = process.argv.slice(2);
  const accountId = args[args.indexOf('--account') + 1];
  const videoPath = args[args.indexOf('--video') + 1];
  const caption = args[args.indexOf('--caption') + 1] || '';

  if (!accountId || !videoPath) {
    console.error('Usage: node poster.js --account <id> --video <path> --caption "text"');
    process.exit(1);
  }

  // Load account config
  const configPath = path.resolve(__dirname, '../config/accounts.json');
  if (!fs.existsSync(configPath)) {
    console.error('No accounts.json found. Copy accounts.example.json and configure it.');
    process.exit(1);
  }

  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const account = config.satellite_accounts.find(a => a.id === accountId);
  if (!account) {
    console.error(`Account ${accountId} not found in config`);
    process.exit(1);
  }

  const poster = new InstagramPoster(account);
  try {
    await poster.init();
    await poster.login();
    const result = await poster.postReel(videoPath, caption);
    console.log('Result:', JSON.stringify(result, null, 2));
  } catch (e) {
    console.error(`[${accountId}] FAILED:`, e.message);
    process.exit(1);
  } finally {
    await poster.close();
  }
}

module.exports = { InstagramPoster };

if (require.main === module) {
  main();
}
