const { chromium } = require('playwright');

async function scrapeGoogleMaps(searchQuery, maxResults = 30) {
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
  console.error(`Navigating to: ${url}`);

  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(8000);

  // Scroll to load more results
  console.error('Scrolling to load more results...');
  for (let i = 0; i < 15; i++) {
    await page.mouse.wheel(0, 3000);
    await page.waitForTimeout(2500);
  }

  // Extract all result links with aria-label (business names) and href
  const results = await page.evaluate(() => {
    const links = Array.from(document.querySelectorAll('a.hfpxzc'));
    const unique = new Map();
    
    links.forEach(link => {
      const name = link.getAttribute('aria-label');
      const href = link.getAttribute('href');
      if (name && href && !unique.has(name)) {
        unique.set(name, href);
      }
    });
    
    return Array.from(unique.entries()).map(([name, href]) => ({ name, href }));
  });

  console.error(`Found ${results.length} businesses. Now extracting details from their pages...`);

  const enriched = [];

  for (let i = 0; i < Math.min(results.length, maxResults); i++) {
    const { name, href } = results[i];
    try {
      console.error(`  [${i+1}/${Math.min(results.length, maxResults)}] Opening: ${name}`);
      
      // Go to the business's Google Maps place page
      await page.goto(href, { waitUntil: 'domcontentloaded', timeout: 20000 });
      await page.waitForTimeout(4000);

      const data = await page.evaluate(() => {
        const result = { website: '', phone: '' };
        
        // Look for website link - often has text "Website" or is an external link
        const links = Array.from(document.querySelectorAll('a[href*="http"]'));
        for (const link of links) {
          const href = link.href;
          // Skip Google internal links
          if (href.includes('google.com/maps') || href.includes('google.com/url')) continue;
          // This is likely the website
          result.website = href;
          break;
        }
        
        // Phone: find any text that looks like a phone number
        const text = document.body.innerText;
        const phoneMatch = text.match(/(\(\d{3}\)\s?\d{3}-\d{4}|\d{3}-\d{3}-\d{4})/);
        if (phoneMatch) result.phone = phoneMatch[0];
        
        return result;
      });

      enriched.push({
        name,
        website: data.website || '',
        phone: data.phone || '',
        has_website: data.website ? true : false
      });

      console.error(`    → Website: ${data.website ? '✓' : '✗'} | Phone: ${data.phone || 'none'}`);
      
    } catch (e) {
      console.error(`  ✗ Error on ${name}: ${e.message}`);
      enriched.push({ name, website: '', phone: '', has_website: false });
    }
  }

  await browser.close();
  return enriched;
}

// Run
const query = process.argv[2] || 'hair salons Minneapolis';
const max = parseInt(process.argv[3]) || 30;

scrapeGoogleMaps(query, max)
  .then(results => {
    // Only JSON on stdout for parsing
    console.log(JSON.stringify(results, null, 2));
  })
  .catch(err => {
    console.error('Error:', err);
    process.exit(1);
  });
