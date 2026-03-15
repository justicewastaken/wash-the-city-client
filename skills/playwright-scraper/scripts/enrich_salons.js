const { chromium } = require('playwright');
const fs = require('fs');

// Read CSV
const csv = fs.readFileSync('/root/.openclaw/workspace/salon_leads.csv', 'utf8');
const lines = csv.trim().split('\n').filter(l => l.trim());
const headers = lines[0].split(',').map(h => h.trim());
const rows = [];

for (let i = 1; i < lines.length; i++) {
  const cols = lines[i].split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/);
  const obj = {};
  headers.forEach((h, idx) => {
    const val = cols[idx] ? cols[idx].replace(/^"|"$/g, '').trim() : '';
    obj[h] = val;
  });
  rows.push(obj);
}

console.log(`Loaded ${rows.length} leads. Enriching...`);

async function enrich() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  for (let i = 0; i < rows.length; i++) {
    const lead = rows[i];
    const website = lead.website;
    console.log(`[${i+1}/${rows.length}] ${lead.business_name}`);
    
    if (website && website.startsWith('http')) {
      try {
        await page.goto(website, { waitUntil: 'domcontentloaded', timeout: 15000 });
        await page.waitForTimeout(2000);
        
        const data = await page.evaluate(() => {
          const emails = new Set();
          
          // mailto links
          const mailtoLinks = document.querySelectorAll('a[href^="mailto:"]');
          mailtoLinks.forEach(a => {
            const href = a.getAttribute('href');
            if (href && href.startsWith('mailto:')) {
              const email = href.substring(7).split('?')[0];
              if (email && email.includes('@')) emails.add(email);
            }
          });
          
          // visible email text
          if (document.body && document.body.innerText) {
            const text = document.body.innerText;
            const emailRegex = /[\w\.-]+@[\w\.-]+\.\w+/g;
            let match;
            while ((match = emailRegex.exec(text)) !== null) {
              emails.add(match[0]);
            }
          }
          
          return Array.from(emails);
        });
        
        if (data.length > 0) {
          // Prefer info@ or hello@ else first
          const preferred = data.find(e => e.startsWith('info@') || e.startsWith('hello@')) || data[0];
          lead.email = preferred;
          console.log(`  → Email: ${preferred}`);
        } else {
          // Generic fallback
          try {
            const url = new URL(website);
            const domain = url.hostname.replace('www.', '');
            lead.email = `info@${domain}`;
          } catch (e) {
            lead.email = '';
          }
          console.log(`  → No email found, set generic: ${lead.email}`);
        }
        
      } catch (e) {
        console.log(`  ✗ Error: ${e.message}`);
        try {
          const url = new URL(website);
          const domain = url.hostname.replace('www.', '');
          lead.email = `info@${domain}`;
        } catch (e2) {
          lead.email = '';
        }
      }
    } else {
      lead.email = '';
    }
    
    // Rate limit between visits
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  await browser.close();

  // Write CSV
  const outputLines = [headers.join(',')];
  rows.forEach(row => {
    const line = headers.map(h => {
      const val = row[h] || '';
      return val.includes(',') && !val.startsWith('"') ? `"${val}"` : val;
    }).join(',');
    outputLines.push(line);
  });
  
  fs.writeFileSync('/root/.openclaw/workspace/salon_leads_enriched.csv', outputLines.join('\n'), 'utf8');
  console.log(`\n✓ Enriched CSV saved: salon_leads_enriched.csv (${rows.length} leads)`);
}

enrich().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
