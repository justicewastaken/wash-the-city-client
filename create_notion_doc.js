const https = require('https');

const NOTION_TOKEN = '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';
const NOTION_VERSION = '2022-06-28';

// Step 1: Create the page
function createPage(callback) {
  const data = JSON.stringify({
    parent: { type: 'workspace' },
    title: [{ type: 'text', text: { content: 'OpenClaw Notion Integration Setup' } }]
  });
  const options = {
    hostname: 'api.notion.com',
    path: '/v1/pages',
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${NOTION_TOKEN}`,
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
        try {
          const json = JSON.parse(body);
          callback(null, json);
        } catch (e) {
          callback(e);
        }
      } else {
        callback(new Error(`HTTP ${res.statusCode}: ${body}`));
      }
    });
  });
  req.on('error', callback);
  req.write(data);
  req.end();
}

// Step 2: Append content blocks to the page
function appendBlocks(pageId, callback) {
  const blocks = [
    {
      object: 'block',
      type: 'heading_1',
      heading_1: { rich_text: [{ type: 'text', text: { content: 'How I Installed the Notion Integration' } }] }
    },
    {
      object: 'block',
      type: 'paragraph',
      paragraph: {
        rich_text: [
          { type: 'text', text: { content: '1. Created an internal integration in Notion (OpenClaw Agent).\n' } },
          { type: 'text', text: { content: '2. Copied the integration token and stored it in /root/.openclaw/credentials/notion.json.\n' } },
          { type: 'text', text: { content: '3. Shared the entire workspace with the integration (Settings → Members → invite OpenClaw Agent).\n' } },
          { type: 'text', text: { content: '4. Verified access by calling the Notion API.\n' } },
          { type: 'text', text: { content: '5. The Notion skill is now ready to read and write pages and databases.' } }
        ]
      }
    },
    {
      object: 'block',
      type: 'heading_2',
      heading_2: { rich_text: [{ type: 'text', text: { content: 'Testing' } }] }
    },
    {
      object: 'block',
      type: 'paragraph',
      paragraph: {
        rich_text: [
          { type: 'text', text: { content: 'The integration token is: ' } },
          { type: 'text', text: { content: NOTION_TOKEN }, annotations: { code: true } }
        ]
      }
    }
  ];
  const data = JSON.stringify({ children: blocks });
  const options = {
    hostname: 'api.notion.com',
    path: `/v1/blocks/${pageId}/children`,
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${NOTION_TOKEN}`,
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
        callback(null);
      } else {
        callback(new Error(`HTTP ${res.statusCode}: ${body}`));
      }
    });
  });
  req.on('error', callback);
  req.write(data);
  req.end();
}

// Main
createPage((err, page) => {
  if (err) {
    console.error('Create page failed:', err.message);
    process.exit(1);
  }
  const pageId = page.id;
  const pageUrl = page.url;
  console.log('Page created:', pageUrl);
  appendBlocks(pageId, err => {
    if (err) {
      console.error('Append blocks failed:', err.message);
      process.exit(1);
    }
    console.log('Documentation added to page.');
    console.log('PAGE_URL=', pageUrl);
    process.exit(0);
  });
});
