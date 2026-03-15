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

  // Extract business names and their place page URLs
  const businesses = await page.evaluate(() => {
    const results = [];
    const links = document.querySelectorAll('a.hfpxzc');
    links.forEach(link => {
      const name = link.getAttribute('aria-label');
      const href = link.getAttribute('href');
      if (name && href && !href.includes('google.com/maps/place/')) {
        results.push({ name, href });
      }
    });
    return results.slice(0, 30);
  });

  console.log(`Found ${businesses.length} businesses. Fetching details from their pages...`);

  const enriched = [];

  for (const biz of businesses) {
    try {
      // Navigate directly to the business's Google Maps place page
      await page.goto(biz.href, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(3000);

      const data = await page.evaluate(() => {
        const result = { name: '', website: '', phone: '' };
        
        // Name from the big title
        const titleEl = document.querySelector('.fontHeadlineLarge, .section-hero-header-title');
        if (titleEl) result.name = titleEl.innerText.trim();
        
        // Website link - look for the "Website" button or any external http link
        const websiteLink = Array.from(document.querySelectorAll('a[href*="http"]')).find(a => 
          !a.href.includes('google.com/maps') && 
          !a.href.includes('google.com/url') &&
          a.innerText.toLowerCase().includes('website') || a.href.includes('http')
        );
        if (websiteLink) {
          // Sometimes it's a redirect URL, follow it to get actual site
          const href = websiteLink.href;
          if (href.includes('/url?q=')) {
            const match = href.match(/\/url\?q=([^&]+)/);
            result.website = match ? decodeURIComponent(match[1]) : href;
          } else {
            result.website = href;
          }
        }
        
        // Phone number
        const text = document.body.innerText;
        const phoneMatch = text.match(/(\(\d{3}\)\s?\d{3}-\d{4}|\d{3}-\d{3}-\d{4})/);
        if (phoneMatch) result.phone = phoneMatch[0];
        
        return result;
      });

      enriched.push({
        name: data.name || biz.name,
        website: data.website || '',
        phone: data.phone || '',
        has_website: data.website ? true : false
      });

      console.log(`  ✓ ${data.name || biz.name} - Website: ${data.website ? 'yes' : 'no'} - Phone: ${data.phone || 'none'}`);
      
    } catch (e) {
      console.log(`  ✗ Error on ${biz.name}: ${e.message}`);
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
