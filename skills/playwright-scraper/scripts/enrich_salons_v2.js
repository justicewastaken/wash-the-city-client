const { chromium } = require('playwright');
const fs = require('fs');

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

console.log(`Enriching ${rows.length} leads...`);

async function enrich() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  for (let i = 0; i < rows.length; i++) {
    const lead = rows[i];
    const website = lead.website;
    // Skip if email already present (non-empty after trim)
    if (lead.email && lead.email.trim() !== '') {
      console.log(`[${i+1}/${rows.length}] ${lead.business_name} - already has email: ${lead.email}, skipping`);
      continue;
    }
    
    if (website && website.startsWith('http')) {
      try {
        await page.goto(website, { waitUntil: 'domcontentloaded', timeout: 15000 });
        await page.waitForTimeout(2500);
        
        const emails = await page.evaluate(() => {
          const found = new Set();
          
          // mailto links
          document.querySelectorAll('a[href^="mailto:"]').forEach(a => {
            const href = a.getAttribute('href');
            if (href) {
              const email = href.split('?')[0].substring(7);
              if (email && email.includes('@')) found.add(email);
            }
          });
          
          // visible email text
          const bodyText = document.body ? document.body.innerText : '';
          const regex = /[\w\.-]+@[\w\.-]+\.\w+/g;
          let m;
          while ((m = regex.exec(bodyText)) !== null) {
            found.add(m[0]);
          }
          
          return Array.from(found);
        });
        
        if (emails.length > 0) {
          // Prefer info@ or hello@ or contact@
          const preferred = emails.find(e => e.startsWith('info@') || e.startsWith('hello@') || e.startsWith('contact@')) || emails[0];
          lead.email = preferred;
          console.log(`  → Email: ${preferred}`);
        } else {
          // Try domain-based fallback
          try {
            const url = new URL(website);
            let domain = url.hostname;
            if (domain.startsWith('www.')) domain = domain.substring(4);
            // If it's a known booking platform domain, we can't guess
            if (['app.squareup.com', 'dashboard.boulevard.io', 'vagaro.com', 'phorest.com', 'na0.meevo.com', 'online.rosysalonsoftware.com', 'booksy.com', 'app.salonrunner.com', 'places.singleplatform.com'].some(d => domain.includes(d))) {
              lead.email = '';
            } else {
              lead.email = `info@${domain}`;
            }
          } catch (e) {
            lead.email = '';
          }
          console.log(`  → Email: ${lead.email || '(none)'}`);
        }
      } catch (e) {
        console.log(`  ✗ Error: ${e.message}`);
        lead.email = '';
      }
    } else {
      lead.email = '';
    }
    
    await new Promise(r => setTimeout(r, 1500));
  }

  await browser.close();

  // Write enriched CSV
  const outLines = [headers.join(',')];
  rows.forEach(r => {
    const line = headers.map(h => {
      const v = r[h] || '';
      return v.includes(',') && !v.startsWith('"') ? `"${v}"` : v;
    }).join(',');
    outLines.push(line);
  });
  
  fs.writeFileSync('/root/.openclaw/workspace/salon_leads_enriched.csv', outLines.join('\n'), 'utf8');
  console.log(`\n✓ Saved enriched leads: salon_leads_enriched.csv`);
}

enrich().catch(err => {
  console.error('Fatal:', err);
  process.exit(1);
});
