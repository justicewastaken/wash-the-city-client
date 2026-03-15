const https = require('https');
const token = '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';
const NOTION_VERSION = '2022-06-28';

// Replace with your page ID if you have it, or we'll list recent pages
// For now, just test making a specific page public (if you provide page ID)
// Or we can create a fresh page and immediately share it

function createPage() {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      parent: { type: 'workspace' },
      title: [{ type: 'text', text: { content: 'OpenClaw Public Test' } }]
    });
    const options = {
      hostname: 'api.notion.com',
      path: '/v1/pages',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Notion-Version': NOTION_VERSION,
        'Content-Length': data.length
      }
    };
    const req = https.request(options, res => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(JSON.parse(body));
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${body}`));
        }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

function makePublic(pageId) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ share: { type: 'public', allow: true } });
    const options = {
      hostname: 'api.notion.com',
      path: `/v1/pages/${pageId}/share`,
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Notion-Version': NOTION_VERSION,
        'Content-Length': data.length
      }
    };
    const req = https.request(options, res => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve();
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${body}`));
        }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

createPage()
  .then(page => {
    console.log('Created page:', page.url);
    return makePublic(page.id).then(() => ({ pageId: page.id, url: page.url }));
  })
  .then(({ pageId, url }) => {
    console.log('Made public:', url);
    console.log('PAGE_ID=', pageId);
    console.log('PAGE_URL=', url);
  })
  .catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
  });
