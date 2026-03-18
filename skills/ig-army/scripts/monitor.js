// scripts/monitor.js
// Monitors the source Instagram account for new reels
// Downloads video + caption to the content bank
// Triggers distribution when new content is detected

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const CONTENT_BANK_DIR = path.resolve(__dirname, '../content-bank');
const MANIFEST_PATH = path.resolve(CONTENT_BANK_DIR, 'manifest.json');
const CONFIG_PATH = path.resolve(__dirname, '../config/accounts.json');

class SourceMonitor {
  constructor() {
    this.config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    this.source = this.config.source_account;
    this.manifest = this.loadManifest();
  }

  loadManifest() {
    if (fs.existsSync(MANIFEST_PATH)) {
      return JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'));
    }
    return { posts: [], last_check: null };
  }

  saveManifest() {
    fs.writeFileSync(MANIFEST_PATH, JSON.stringify(this.manifest, null, 2));
  }

  async checkForNewPosts() {
    console.log(`[Monitor] Checking ${this.source.username} for new posts...`);

    const browser = await chromium.launch({ headless: true });
    const sessionPath = path.resolve(__dirname, '..', this.source.session_file);

    const contextOptions = {
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
      viewport: { width: 1366, height: 768 },
    };

    if (fs.existsSync(sessionPath)) {
      contextOptions.storageState = JSON.parse(fs.readFileSync(sessionPath, 'utf8'));
    }

    const context = await browser.newContext(contextOptions);
    const page = await context.newPage();

    try {
      // Go to source account's profile
      await page.goto(`https://www.instagram.com/${this.source.username}/`, {
        waitUntil: 'networkidle',
      });
      await page.waitForTimeout(3000);

      // Get reels tab or recent posts
      // We intercept the GraphQL responses to get post data
      const posts = [];

      // Scrape the most recent posts from the profile grid
      const postLinks = await page.$$eval('a[href*="/reel/"], a[href*="/p/"]', (links) =>
        links.slice(0, 6).map(link => ({
          href: link.href,
          shortcode: link.href.match(/\/(reel|p)\/([^/]+)/)?.[2] || null,
        }))
      );

      console.log(`[Monitor] Found ${postLinks.length} recent posts`);

      // Check which posts are new (not in manifest)
      const knownShortcodes = new Set(this.manifest.posts.map(p => p.shortcode));
      const newPosts = postLinks.filter(p => p.shortcode && !knownShortcodes.has(p.shortcode));

      if (newPosts.length === 0) {
        console.log('[Monitor] No new posts found');
        this.manifest.last_check = new Date().toISOString();
        this.saveManifest();
        return [];
      }

      console.log(`[Monitor] ${newPosts.length} new post(s) detected!`);

      // For each new post, navigate to it and extract video + caption
      for (const post of newPosts) {
        try {
          const postData = await this.extractPostData(page, post);
          if (postData) {
            posts.push(postData);
          }
        } catch (e) {
          console.error(`[Monitor] Failed to extract post ${post.shortcode}:`, e.message);
        }
      }

      // Save session
      const storageState = await context.storageState();
      fs.writeFileSync(sessionPath, JSON.stringify(storageState, null, 2));

      return posts;
    } finally {
      await browser.close();
    }
  }

  async extractPostData(page, post) {
    console.log(`[Monitor] Extracting data for ${post.shortcode}...`);
    await page.goto(post.href, { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);

    // Extract caption
    let caption = '';
    try {
      const captionEl = await page.$('h1, span[class*="caption"], div[class*="caption"]');
      if (captionEl) {
        caption = await captionEl.innerText();
      }
    } catch (e) {
      console.warn(`[Monitor] Could not extract caption for ${post.shortcode}`);
    }

    // Extract video URL from the page source or video element
    let videoUrl = null;
    try {
      videoUrl = await page.$eval('video source, video', (el) => {
        return el.src || el.querySelector('source')?.src || null;
      });
    } catch (e) {
      console.warn(`[Monitor] Could not find video element for ${post.shortcode}`);
    }

    if (!videoUrl) {
      // Try intercepting network requests for the video
      console.log(`[Monitor] Attempting network interception for video URL...`);
      // Fallback: use yt-dlp or similar to download
      try {
        const outputPath = path.join(CONTENT_BANK_DIR, `${post.shortcode}.mp4`);
        execSync(`yt-dlp -o "${outputPath}" "${post.href}" 2>/dev/null`, { timeout: 60000 });
        if (fs.existsSync(outputPath)) {
          console.log(`[Monitor] Downloaded via yt-dlp: ${post.shortcode}`);
          return this.registerPost(post.shortcode, outputPath, caption);
        }
      } catch (e) {
        console.error(`[Monitor] yt-dlp fallback failed for ${post.shortcode}`);
      }
      return null;
    }

    // Download the video
    const outputPath = path.join(CONTENT_BANK_DIR, `${post.shortcode}.mp4`);
    const response = await page.context().request.get(videoUrl);
    const buffer = await response.body();
    fs.writeFileSync(outputPath, buffer);
    console.log(`[Monitor] Downloaded: ${post.shortcode} (${(buffer.length / 1024 / 1024).toFixed(1)}MB)`);

    return this.registerPost(post.shortcode, outputPath, caption);
  }

  registerPost(shortcode, videoPath, caption) {
    const postEntry = {
      shortcode,
      video_file: path.basename(videoPath),
      caption,
      discovered_at: new Date().toISOString(),
      distributed: false,
      distribution_results: [],
    };

    this.manifest.posts.push(postEntry);
    this.manifest.last_check = new Date().toISOString();
    this.saveManifest();

    return postEntry;
  }
}

// CLI usage
async function main() {
  const monitor = new SourceMonitor();
  const newPosts = await monitor.checkForNewPosts();

  if (newPosts.length > 0) {
    console.log('\n--- New posts ready for distribution ---');
    newPosts.forEach(p => {
      console.log(`  ${p.shortcode}: ${p.caption.substring(0, 50)}...`);
    });
    console.log('\nRun distributor.js to push these to satellite accounts.');
  }
}

module.exports = { SourceMonitor };

if (require.main === module) {
  main();
}
