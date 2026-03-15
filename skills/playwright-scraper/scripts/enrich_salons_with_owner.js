const { chromium } = require('playwright');
const fs = require('fs');

const csvPath = '/root/.openclaw/workspace/salon_leads.csv';
const outPath = '/root/.openclaw/workspace/salon_leads_enriched.csv';

const csv = fs.readFileSync(csvPath, 'utf8');
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

console.log(`Enriching ${rows.length} leads with email AND owner name...`);

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
    
    // Default fallbacks
    lead.email = '';
    lead.owner_first_name = '';
    
    if (website && website.startsWith('http')) {
      try {
        await page.goto(website, { waitUntil: 'domcontentloaded', timeout: 15000 });
        await page.waitForTimeout(2000);
        
        const data = await page.evaluate(() => {
          const emails = new Set();
          
          // mailto links
          document.querySelectorAll('a[href^="mailto:"]').forEach(a => {
            const href = a.getAttribute('href');
            if (href) {
              const email = href.split('?')[0].substring(7);
              if (email && email.includes('@')) emails.add(email);
            }
          });
          
          // visible email text
          const bodyText = document.body ? document.body.innerText : '';
          const emailRegex = /[\w\.-]+@[\w\.-]+\.\w+/g;
          let m;
          while ((m = emailRegex.exec(bodyText)) !== null) {
            emails.add(m[0]);
          }
          
          // Owner name search: look for patterns like "Owner: Jane", "Founder - John", "Managed by Sarah"
          let ownerName = '';
          const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
          const nodes = [];
          while (walker.nextNode()) {
            nodes.push(walker.currentNode);
          }
          
          for (const node of nodes) {
            const text = node.textContent.trim();
            if (!text) continue;
            const lower = text.toLowerCase();
            if (lower.includes('owner') || lower.includes('founder') || lower.includes('manager') || lower.includes('proprietor')) {
              // Extract potential name: take words after these keywords
              const words = text.split(/\s+/);
              const idx = words.findIndex(w => /owner|founder|manager|proprietor/i.test(w));
              if (idx !== -1 && words[idx + 1]) {
                // Clean: remove punctuation and any trailing words like "is", "at", etc.
                let candidate = words[idx + 1].replace(/[^a-zA-Z]/g, '');
                if (candidate.length > 1 && candidate.length < 20) {
                  ownerName = candidate;
                  break;
                }
              }
            }
          }
          
          return {
            emails: Array.from(emails),
            ownerName: ownerName
          };
        });
        
        if (data.emails.length > 0) {
          const preferred = data.emails.find(e => e.startsWith('info@') || e.startsWith('hello@') || e.startsWith('contact@')) || data.emails[0];
          lead.email = preferred;
          console.log(`  → Email: ${preferred}`);
        } else {
          // Domain fallback for non-booking platform sites
          try {
            const url = new URL(website);
            let domain = url.hostname.replace('www.', '');
            const blockedDomains = ['app.squareup.com', 'dashboard.boulevard.io', 'vagaro.com', 'phorest.com', 'na0.meevo.com', 'online.rosysalonsoftware.com', 'booksy.com', 'app.salonrunner.com', 'places.singleplatform.com', 'the Reflect salon site'];
            if (blockedDomains.every(d => !domain.includes(d))) {
              lead.email = `info@${domain}`;
            }
          } catch (e) {}
        }
        
        if (data.ownerName) {
          lead.owner_first_name = data.ownerName;
          console.log(`  → Owner: ${data.ownerName}`);
        }
        
      } catch (e) {
        console.log(`  ✗ Error: ${e.message}`);
      }
    }
    
    // Rate limit to avoid overwhelming
    await new Promise(resolve => setTimeout(resolve, 1500));
  }

  await browser.close();

  // Write to CSV
  const outLines = [headers.join(',') + ',owner_first_name,email_auto_filled']; // add new columns if needed
  rows.forEach(r => {
    const line = headers.map(h => {
      const v = r[h] || '';
      return v.includes(',') && !v.startsWith('"') ? `"${v}"` : v;
    }).join(',');
    outLines.push(line);
  });
  
  fs.writeFileSync(outPath, outLines.join('\n'), 'utf8');
  console.log(`\n✓ Enriched CSV saved with ${rows.length} leads`);
}

enrich().catch(err => {
  console.error('Fatal:', err);
  process.exit(1);
});
