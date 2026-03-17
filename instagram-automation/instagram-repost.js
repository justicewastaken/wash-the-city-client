/**
 * Instagram Repost Automation
 *
 * Scrapes top 3 Explore reels (>100k likes) and reposts them with a fixed caption.
 * Uses persistent browser session to stay logged in.
 *
 * Usage:
 *   node instagram-repost.js
 *
 * First run will prompt for login; session is saved to 'instagram_session' directory.
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// CONFIGURATION
const CONFIG = {
  // Your Instagram credentials (will be prompted if not set)
  username: process.env.IG_USERNAME || '',
  password: process.env.IG_PASSWORD || '',
  // Fixed caption for all reposts
  caption: `[Your fixed caption here]`,
  // Minimum likes for reels to consider
  minLikes: 100000,
  // How many reels to repost per run
  maxReposts: 3,
  // File paths
  sessionDir: './instagram_session',
  stateFile: './state.json',
  downloadDir: './downloads'
};

// Ensure directories exist
[CONFIG.sessionDir, CONFIG.downloadDir].forEach(dir => {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
});

async function humanDelay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms + Math.random() * ms));
}

async function loginIfNeeded(page) {
  // Check if already logged in by seeing if explore page loads without login prompt
  await page.goto('https://www.instagram.com/explore/', { waitUntil: 'networkidle2' });
  
  // Look for login form or "Accept All Cookies" etc.
  const loginForm = await page.$('form[method="POST"]');
  if (loginForm) {
    console.log('Login required. Attempting to log in...');
    await page.waitForSelector('input[name="username"]');
    await page.type('input[name="username"]', CONFIG.username, { delay: 50 });
    await page.type('input[name="password"]', CONFIG.password, { delay: 50 });
    await page.click('button[type="submit"]');
    await humanDelay(3000);
    
    // Handle "Save Info" and "Turn on Notifications" popups if they appear
    const buttons = await page.$$('button');
    for (const btn of buttons) {
      const text = await btn.evaluate(b => b.textContent || '');
      if (text.includes('Not Now') || text.includes('Cancel') || text.includes('Skip')) {
        try { await btn.click(); await humanDelay(1000); } catch(e){}
      }
    }
    console.log('Login attempted. Session will be saved.');
  } else {
    console.log('Already logged in (session persisted).');
  }
}

async function scrapeTopReels(page) {
  console.log('Scraping Explore page for top reels...');
  await page.goto('https://www.instagram.com/explore/', { waitUntil: 'networkidle2' });
  await humanDelay(2000);

  // Scroll to load more reels
  for (let i = 0; i < 5; i++) {
    await page.evaluate(() => window.scrollBy(0, 1000));
    await humanDelay(2000);
  }

  // Find reels with high like counts
  // This is fragile; we'll look for reel links and their like counts in the DOM
  const reels = await page.$$('article a[href*="/reel/"]');
  console.log(`Found ${reels.length} reel links.`);
  
  const candidates = [];
  for (const reel of reels) {
    try {
      const href = await reel.getAttribute('href');
      const url = `https://www.instagram.com${href}`;
      
      // Open in new tab to get like count
      const page2 = await page.browser().newPage();
      await page2.goto(url, { waitUntil: 'networkidle2' });
      await humanDelay(1000);
      
      // Try to find like count element (varies by page structure)
      const likeText = await page2.evaluate(() => {
        const el = document.querySelector('span[data-testid="like-count"]') || 
                   document.querySelector('div > span > span') ||
                   document.querySelector('section main div div div:nth-child(2) span span');
        return el ? el.textContent : '';
      });
      await page2.close();
      
      const likes = parseLikes(likeText);
      if (likes >= CONFIG.minLikes) {
        candidates.push({ url, likes });
      }
    } catch (e) {
      console.log('Error scraping a reel:', e.message);
    }
  }

  // Sort by likes descending and take top N
  candidates.sort((a, b) => b.likes - a.likes);
  return candidates.slice(0, CONFIG.maxReposts);
}

function parseLikes(text) {
  // Convert "123K", "1.5M" to numbers
  if (!text) return 0;
  text = text.replace(/,/g, '').toLowerCase();
  if (text.includes('k')) return parseFloat(text) * 1000;
  if (text.includes('m')) return parseFloat(text) * 1000000;
  const num = parseFloat(text);
  return isNaN(num) ? 0 : num;
}

async function downloadVideo(page, reelUrl) {
  await page.goto(reelUrl, { waitUntil: 'networkidle2' });
  await humanDelay(1000);
  
  // Find video element
  const videoSrc = await page.evaluate(() => {
    const video = document.querySelector('video');
    return video ? video.src : null;
  });
  
  if (!videoSrc) {
    throw new Error('No video found on page');
  }
  
  // Download video
  const filename = path.join(CONFIG.downloadDir, `reel_${Date.now()}.mp4`);
  const response = await page.goto(videoSrc);
  const buffer = await response.buffer();
  fs.writeFileSync(filename, buffer);
  console.log(`Downloaded video to ${filename}`);
  return filename;
}

async function createPost(page, videoPath, caption) {
  // Click "+" button to upload (this is simplified; actual clicks vary)
  await page.goto('https://www.instagram.com/create/style/', { waitUntil: 'networkidle2' });
  await humanDelay(2000);
  
  // Upload file
  const input = await page.$('input[type="file"]');
  if (!input) throw new Error('File input not found');
  await input.uploadFile(path.resolve(videoPath));
  await humanDelay(3000);
  
  // Add caption
  const captionArea = await page.$('div[contenteditable="true"]');
  if (captionArea) {
    await captionArea.click();
    await humanDelay(500);
    await page.keyboard.type(caption);
    await humanDelay(500);
  }
  
  // Share/Post button
  const shareBtn = await page.$('button:has-text("Share")') || await page.$('button:has-text("Post")');
  if (shareBtn) {
    await shareBtn.click();
    await humanDelay(2000);
    console.log('Post created.');
  } else {
    console.log('Could not find share button.');
  }
}

async function main() {
  if (!CONFIG.username || !CONFIG.password) {
    console.log('Please set IG_USERNAME and IG_PASSWORD environment variables, or edit the script.');
    process.exit(1);
  }

  const browser = await puppeteer.launch({
    headless: false, // Set true for no UI, but may trigger more bot detection
    userDataDir: CONFIG.sessionDir,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 800 });
  await humanDelay(1000);

  try {
    await loginIfNeeded(page);
    const topReels = await scrapeTopReels(page);
    console.log(`Selected ${topReels.length} reels to repost:`);
    topReels.forEach((r, i) => console.log(`${i+1}. ${r.url} (${r.likes.toLocaleString()} likes)`));

    for (const [index, reel] of topReels.entries()) {
      console.log(`\n[${index+1}/${topReels.length}] Reposting: ${reel.url}`);
      try {
        const videoPath = await downloadVideo(page, reel.url);
        await createPost(page, videoPath, CONFIG.caption);
        // Cleanup downloaded file
        fs.unlinkSync(videoPath);
        await humanDelay(5000); // Wait between posts
      } catch (e) {
        console.error(`Failed to repost ${reel.url}:`, e.message);
      }
    }
  } finally {
    await browser.close();
  }
}

main().catch(console.error);
