const https = require('https');
const fs = require('fs');
const path = require('path');

// Optimized prompt for Pollinations - aiming for native TikTok look
const prompt = 'candid iPhone photo, golden retriever dog sitting on couch wearing personalized pet jewelry necklace, warm living room lighting, shallow depth of field, slight grain, 18-year-old female dog mom taking selfie with dog, cozy aesthetic';

const outPath = path.join(__dirname, 'output', 'pupjewelry_slide_1.jpg');

function generate() {
  const encoded = encodeURIComponent(prompt);
  const url = `https://image.pollinations.ai/prompt/${encoded}?width=1024&height=1024&nologo=true&seed=${Date.now()}&model=flux`;
  
  https.get(url, (res) => {
    if (res.statusCode !== 200) {
      console.error('Bad status:', res.statusCode);
      res.resume();
      return;
    }
    const stream = fs.createWriteStream(outPath);
    res.pipe(stream);
    stream.on('finish', () => {
      console.log('Image saved:', outPath);
      // After image download, we create overlay version
      createOverlay(outPath, path.join(__dirname, 'output', 'pupjewelry_slide_1_overlay.png'));
    });
    stream.on('error', e => console.error('Write error:', e));
  }).on('error', e => console.error('Request error:', e));
}

function createOverlay(inputImg, outputImg) {
  const { createCanvas, loadImage } = require('canvas');
  (async () => {
    try {
      const img = await loadImage(inputImg);
      const canvas = createCanvas(img.width, img.height);
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0);

      const padding = 60;
      const maxWidth = img.width - padding * 2;
      const lineHeight = 60;
      const fontSize = 52;
      ctx.font = `bold ${fontSize}px Arial`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#FFFFFF';
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 3;
      ctx.lineJoin = 'round';

      function drawText(text, y) {
        const words = text.split(' ');
        let lines = [];
        let line = '';
        for (const word of words) {
          const test = line ? line + ' ' + word : word;
          if (ctx.measureText(test).width > maxWidth) {
            lines.push(line);
            line = word;
          } else {
            line = test;
          }
        }
        if (line) lines.push(line);
        lines.forEach((l, i) => {
          const yPos = y - ((lines.length - 1) * lineHeight / 2) + (i * lineHeight);
          ctx.strokeText(l, img.width / 2, yPos);
          ctx.fillText(l, img.width / 2, yPos);
        });
      }

      // Top hook
      drawText("When your dog asks for a second date 😂", padding + lineHeight / 2 + 20);
      // Bottom CTA
      drawText("PupJewelry.com • Link in bio", img.height - padding - lineHeight / 2 - 20);

      const buf = canvas.toBuffer('image/png');
      fs.writeFileSync(outputImg, buf);
      console.log('Final slide with overlay:', outputImg);
    } catch (e) {
      console.error('Overlay error:', e);
    }
  })();
}

generate();
