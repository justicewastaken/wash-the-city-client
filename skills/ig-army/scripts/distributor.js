// scripts/distributor.js
// Takes undistributed content from the bank and posts to all active satellite accounts
// Staggers posts with randomized delays to avoid detection patterns

const fs = require('fs');
const path = require('path');
const { InstagramPoster } = require('./poster');

const MANIFEST_PATH = path.resolve(__dirname, '../content-bank/manifest.json');
const CONFIG_PATH = path.resolve(__dirname, '../config/accounts.json');
const LOG_DIR = path.resolve(__dirname, '../logs');

class Distributor {
  constructor(options = {}) {
    this.config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    this.manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'));
    this.options = {
      minDelay: 60000,       // 1 min minimum between posts
      maxDelay: 300000,      // 5 min maximum between posts
      maxRetries: 2,         // retry failed posts
      batchSize: 10,         // process N accounts then take a longer break
      batchBreak: 600000,    // 10 min break between batches
      headless: true,
      ...options,
    };
  }

  getActiveAccounts() {
    return this.config.satellite_accounts.filter(a => a.status === 'active');
  }

  getUndistributedPosts() {
    return this.manifest.posts.filter(p => !p.distributed);
  }

  async distributePost(post) {
    const accounts = this.getActiveAccounts();
    if (accounts.length === 0) {
      console.log('[Distributor] No active accounts found');
      return;
    }

    const videoPath = path.resolve(__dirname, '../content-bank', post.video_file);
    if (!fs.existsSync(videoPath)) {
      console.error(`[Distributor] Video file missing: ${post.video_file}`);
      return;
    }

    console.log(`\n${'='.repeat(60)}`);
    console.log(`[Distributor] Distributing: ${post.shortcode}`);
    console.log(`[Distributor] Caption: ${post.caption.substring(0, 80)}...`);
    console.log(`[Distributor] Target accounts: ${accounts.length}`);
    console.log(`${'='.repeat(60)}\n`);

    // Shuffle accounts to randomize posting order each time
    const shuffled = this.shuffleArray([...accounts]);
    const results = [];
    let successCount = 0;
    let failCount = 0;

    for (let i = 0; i < shuffled.length; i++) {
      const account = shuffled[i];

      // Batch break
      if (i > 0 && i % this.options.batchSize === 0) {
        const batchBreak = this.randomBetween(
          this.options.batchBreak * 0.8,
          this.options.batchBreak * 1.2
        );
        console.log(`\n[Distributor] Batch break: ${(batchBreak / 60000).toFixed(1)} minutes...\n`);
        await this.sleep(batchBreak);
      }

      // Post to this account
      const result = await this.postToAccount(account, videoPath, post.caption);
      results.push(result);

      if (result.success) {
        successCount++;
        console.log(`[Distributor] (${i + 1}/${shuffled.length}) ${account.id}: SUCCESS`);
      } else {
        failCount++;
        console.log(`[Distributor] (${i + 1}/${shuffled.length}) ${account.id}: FAILED - ${result.error}`);
      }

      // Random delay before next account
      if (i < shuffled.length - 1) {
        const delay = this.randomBetween(this.options.minDelay, this.options.maxDelay);
        console.log(`[Distributor] Waiting ${(delay / 1000).toFixed(0)}s before next account...`);
        await this.sleep(delay);
      }
    }

    // Update manifest
    post.distributed = true;
    post.distribution_results = results;
    post.distributed_at = new Date().toISOString();
    this.saveManifest();

    // Log results
    this.logDistribution(post, results);

    console.log(`\n${'='.repeat(60)}`);
    console.log(`[Distributor] Distribution complete for ${post.shortcode}`);
    console.log(`[Distributor] Success: ${successCount} | Failed: ${failCount} | Total: ${shuffled.length}`);
    console.log(`${'='.repeat(60)}\n`);

    return { successCount, failCount, total: shuffled.length };
  }

  async postToAccount(account, videoPath, caption, attempt = 1) {
    const poster = new InstagramPoster(account, { headless: this.options.headless });

    try {
      await poster.init();
      await poster.login();
      const result = await poster.postReel(videoPath, caption);

      // Update account's last_post timestamp in config
      account.last_post = new Date().toISOString();
      this.saveConfig();

      return { ...result, success: true };
    } catch (e) {
      console.error(`[${account.id}] Attempt ${attempt} failed: ${e.message}`);

      if (attempt < this.options.maxRetries) {
        console.log(`[${account.id}] Retrying in 30s...`);
        await this.sleep(30000);
        return this.postToAccount(account, videoPath, caption, attempt + 1);
      }

      // Mark account for review if it keeps failing
      if (account.consecutive_failures) {
        account.consecutive_failures++;
      } else {
        account.consecutive_failures = 1;
      }

      // Auto-disable after 3 consecutive failures
      if (account.consecutive_failures >= 3) {
        console.warn(`[${account.id}] 3+ consecutive failures, marking as needs_review`);
        account.status = 'needs_review';
      }
      this.saveConfig();

      return {
        success: false,
        account: account.id,
        error: e.message,
        timestamp: new Date().toISOString(),
      };
    } finally {
      await poster.close();
    }
  }

  async distributeAll() {
    const undistributed = this.getUndistributedPosts();
    if (undistributed.length === 0) {
      console.log('[Distributor] No undistributed content found');
      return;
    }

    console.log(`[Distributor] Found ${undistributed.length} post(s) to distribute`);

    for (const post of undistributed) {
      await this.distributePost(post);
      // Longer break between different posts
      if (undistributed.indexOf(post) < undistributed.length - 1) {
        const breakTime = this.randomBetween(900000, 1800000); // 15-30 min
        console.log(`[Distributor] Break between posts: ${(breakTime / 60000).toFixed(0)} min`);
        await this.sleep(breakTime);
      }
    }
  }

  logDistribution(post, results) {
    if (!fs.existsSync(LOG_DIR)) {
      fs.mkdirSync(LOG_DIR, { recursive: true });
    }

    const logEntry = {
      shortcode: post.shortcode,
      distributed_at: new Date().toISOString(),
      total_accounts: results.length,
      successes: results.filter(r => r.success).length,
      failures: results.filter(r => !r.success).length,
      results,
    };

    const logFile = path.join(LOG_DIR, `dist_${post.shortcode}_${Date.now()}.json`);
    fs.writeFileSync(logFile, JSON.stringify(logEntry, null, 2));

    // Also append to daily summary log
    const dailyLog = path.join(LOG_DIR, `daily_${new Date().toISOString().split('T')[0]}.jsonl`);
    fs.appendFileSync(dailyLog, JSON.stringify(logEntry) + '\n');
  }

  saveManifest() {
    fs.writeFileSync(MANIFEST_PATH, JSON.stringify(this.manifest, null, 2));
  }

  saveConfig() {
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(this.config, null, 2));
  }

  shuffleArray(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  randomBetween(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// CLI usage
async function main() {
  const args = process.argv.slice(2);
  const distributor = new Distributor({
    headless: !args.includes('--visible'),
  });

  if (args.includes('--post')) {
    const shortcode = args[args.indexOf('--post') + 1];
    const post = distributor.manifest.posts.find(p => p.shortcode === shortcode);
    if (!post) {
      console.error(`Post ${shortcode} not found in manifest`);
      process.exit(1);
    }
    await distributor.distributePost(post);
  } else {
    await distributor.distributeAll();
  }
}

module.exports = { Distributor };

if (require.main === module) {
  main();
}
