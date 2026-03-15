const { chromium } = require('playwright');

async function scrapeGoogleMapsDetailed(searchQuery, maxResults = 30) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 800 }
  });
  const page = await context.newPage();

  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
  });

  const encodedQuery = encodeURIComponent(searchQuery);
  const url = `https://www.google.com/maps/search/${encodedQuery}`;
  console.log(`Navigating to: ${url}`);

  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(5000);

  // Scroll to load more results
  for (let i = 0; i < 8; i++) {
    await page.mouse.wheel(0, 3000);
    await page.waitForTimeout(3000);
  }

  // Extract business names from the search results
  const names = await page.evaluate(() => {
    const items = document.querySelectorAll('[jsaction] .fontHeadlineSmall');
    const unique = new Set();
    const result = [];
    items.forEach(el => {
      const name = el.innerText.trim();
      if (name && !unique.has(name) && result.length < 30) {
        unique.add(name);
        result.push(name);
      }
    });
    return result;
  });

  console.log(`Found ${names.length} businesses. Getting details...`);

  const enriched = [];

  for (const name of names) {
    try {
      // Find the clickable element for this business by its name text
      const element = await page.$(`[jsaction] .fontHeadlineSmall:has-text("${name}")`);
      if (!element) {
        console.log(`  ✗ Could not find clickable element for: ${name}`);
        continue;
      }
      await element.click();
      await page.waitForTimeout(2500); // Wait for panel to load

      // Extract details from the opened panel
      const data = await page.evaluate((bizName) => {
        const result = { name: bizName, website: '', phone: '' };
        
        // Website link (external only)
        const links = document.querySelectorAll('a[href*="http"]');
        for (const link of links) {
          const href = link.href;
          if (!href.includes('google.com/maps') && !href.includes('google.com/url')) {
            result.website = href;
            break;
          }
        }
        
        // Phone number from visible text
        const text = document.body.innerText;
        const phoneMatch = text.match(/(\(\d{3}\)\s?\d{3}-\d{4}|\d{3}-\d{3}-\d{4})/);
        if (phoneMatch) result.phone = phoneMatch[0];
        
        return result;
      })(name);

      enriched.push({
        name: data.name,
        website: data.website,
        phone: data.phone,
        has_website: data.website ? true : false
      });

      console.log(`  ✓ ${data.name} - Website: ${data.website ? 'yes' : 'no'} - Phone: ${data.phone || 'none'}`);
      
      // Close panel
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);
      
    } catch (e) {
      console.log(`  ✗ Error on ${name}: ${e.message}`);
    }
  }

  await browser.close();
  return enriched;
}

// Run
const query = process.argv[2] || 'hair salons Minneapolis';
const max = parseInt(process.argv[3]) || 30;

scrapeGoogleMapsDetailed(query, max)
  .then(results => {
    console.log(JSON.stringify(results, null, 2));
  })
  .catch(err => {
    console.error('Error:', err);
    process.exit(1);
  });
