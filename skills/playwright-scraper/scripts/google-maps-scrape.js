const { chromium } = require('playwright');

async function scrapeGoogleMaps(searchQuery, maxResults = 50) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 800 }
  });
  const page = await context.newPage();

  // Add stealth: hide webdriver
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
  });

  const encodedQuery = encodeURIComponent(searchQuery);
  const url = `https://www.google.com/maps/search/${encodedQuery}`;
  console.log(`Navigating to: ${url}`);

  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });

  // Wait for results to load - scroll a few times
  await page.waitForTimeout(5000);

  // Scroll to load more results
  for (let i = 0; i < 5; i++) {
    await page.mouse.wheel(0, 2000);
    await page.waitForTimeout(2000);
  }

  // Extract business data from the page
  const results = await page.evaluate(() => {
    const businesses = [];
    // Google Maps uses various selectors; try to find result items
    const items = document.querySelectorAll('[jsaction*="mouseover"], [jsaction*="click"]');
    
    items.forEach((item, index) => {
      if (businesses.length >= 50) return;
      
      try {
        const nameEl = item.querySelector('.fontHeadlineSmall') || item.querySelector('.Nv2PK');
        const name = nameEl ? nameEl.innerText.trim() : null;
        
        if (!name) return;
        
        // Try to find website link
        const websiteEl = item.querySelector('a[href*="http"]');
        const website = websiteEl ? websiteEl.href : null;
        
        // Try to find phone
        const phoneText = item.innerText;
        const phoneMatch = phoneText.match(/(\(\d{3}\)\s?\d{3}-\d{4}|\d{3}-\d{3}-\d{4})/);
        const phone = phoneMatch ? phoneMatch[0] : null;
        
        businesses.push({
          name,
          website: website || '',
          phone: phone || '',
          has_website: website ? true : false
        });
      } catch (e) {
        // skip
      }
    });
    
    return businesses;
  });

  await browser.close();
  return results;
}

// Usage
const query = process.argv[2] || 'hair salons Minneapolis';
scrapeGoogleMaps(query, 50)
  .then(results => {
    console.log(JSON.stringify(results, null, 2));
  })
  .catch(err => {
    console.error(err);
    process.exit(1);
  });
