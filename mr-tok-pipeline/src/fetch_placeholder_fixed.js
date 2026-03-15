const https = require('https');
const fs = require('fs');
const path = require('path');

const outPath = path.join(process.cwd(), 'output', 'base_image.jpg');

function fetch(url, out) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      if (res.statusCode !== 200) {
        reject(new Error(`HTTP ${res.statusCode}`));
        return;
      }
      const stream = fs.createWriteStream(out);
      res.pipe(stream);
      stream.on('finish', () => resolve(out));
      stream.on('error', reject);
    }).on('error', reject);
  });
}

// Try picsum as fallback
fetch('https://picsum.photos/1024/1024', outPath)
  .then(() => {
    console.log('Placeholder image downloaded:', outPath);
    process.exit(0);
  })
  .catch(err => {
    console.error('Failed to fetch placeholder:', err.message);
    process.exit(1);
  });
