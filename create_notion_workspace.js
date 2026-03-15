const https = require('https');
const token = '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';
const NOTION_VERSION = '2022-06-28';

function createPage() {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      parent: { workspace: true },
      title: [{ type: 'text', text: { content: 'OpenClaw Public Page' } }],
      children: [
        {
          object: 'block',
          type: 'paragraph',
          paragraph: {
            rich_text: [{ type: 'text', text: { content: 'This page is public.' } }]
          }
        }
      ]
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

function sharePage(pageId) {
  return new Promise((resolve', reject) => {
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
    console.log('Created:', page.url);
    return sharePage(page.id).then(() => page.url);
  })
  .then(url => {
    console.log('PUBLIC_URL=' + url);
    const fs = require('fs');
    fs.writeFileSync('notion_public_url.txt', url);
  })
  .catch(err => {
    console.error('ERROR:', err.message);
    process.exit(1);
  });
