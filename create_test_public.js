const https = require('https');
const token = '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';
const NOTION_VERSION = '2022-06-28';

// Create page
function createPage() {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      parent: { type: 'workspace' },
      properties: {},
      children: [
        {
          object: 'block',
          type: 'paragraph',
          paragraph: {
            rich_text: [{ type: 'text', text: { content: 'Test page' } }]
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

// Share page
function sharePage(pageId) {
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
    console.log('Page created, id:', page.id, 'url:', page.url);
    return sharePage(page.id).then(() => page);
  })
  .then(page => {
    console.log('Public URL:', page.url);
    console.log('PAGE_URL=' + page.url);
    const fs = require('fs');
    fs.writeFileSync('notion_public_url.txt', page.url);
  })
  .catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
  });
