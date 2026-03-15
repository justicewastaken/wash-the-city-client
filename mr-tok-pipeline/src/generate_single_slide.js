const fs = require('fs');
const path = require('path');
const https = require('https');
const { createCanvas, loadImage } = require('canvas');

const OUTPUT_DIR = path.join(__dirname, 'output');

// Our scene and persona
const prompt = `From the lens of a warm candid iphone shots: iPhone photo from first-person perspective, walking a golden retriever on leash at night on a residential street. Streetlights cast warm glow. Slightly imperfect framing, natural low-light grain. product: Personalized Pet Jewelry`;

const filename = `slide_${Date.now()}.jpg`;
const imagePath = path.join(OUTPUT_DIR, filename);

// Generate image via Pollinations
function generateImage(prompt, outPath) {
  return new Promise((resolve, reject) => {
    const encoded = encodeURIComponent(prompt);
    const url = `https://image.pollinations.ai/prompt/${encoded}?width=1024&height=1024&nologo=true&seed=${Date.now()}`;
    https.get(url, (res) => {
      if (res.statusCode !== 200) {
        return reject(new Error(`HTTP ${res.statusCode}`));
      }
      const stream = fs.createWriteStream(outPath);
      res.pipe(stream);
      stream.on('finish', () => resolve(outPath));
      stream.on('error', reject);
    }).on('error', reject);
  });
}

// Add text overlay using canvas
function addOverlay(inputPath, outputPath, topText, bottomText) {
  const img = loadImage(inputPath);
  const canvas = createCanvas(img.width, img.height);
  const ctx = canvas.getContext('2d');
  ctx.drawImage(img, 0, 0);

  const padding = 60;
  const maxWidth = img.width - padding * 2;
  const lineHeight = 60;
  const fontSize = 52;
  ctx.font = `bold ${fontSize}px Arial`; // Use system font to avoid missing font
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillStyle = '#FFFFFF';
  ctx.strokeStyle = '#000000';
  ctx.lineWidth = 3;
  ctx.lineJoin = 'round';

  function drawText(text, y) {
    // Simple word wrap
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

  // Top text (hook)
  if (topText) drawText(topText, padding + lineHeight / 2 + 20);
  // Bottom text (CTA)
  if (bottomText) drawText(bottomText, img.height - padding - lineHeight / 2 - 20);

  const buf = canvas.toBuffer('jpg');
  fs.writeFileSync(outputPath, buf);
  console.log(`Overlay added: ${outputPath}`);
}

// Main
(async () => {
  try {
    console.log('Generating image...');
    await generateImage(prompt, imagePath);
    console.log('Image generated:', imagePath);

    const finalPath = path.join(OUTPUT_DIR, 'final_' + filename);
    addOverlay(imagePath, finalPath, 'When your dog asks for a second date 😂', 'PupJewelry.com • Link in bio');

    console.log('Final slide:', finalPath);
    // Read and return the image data path
    process.exit(0);
  } catch (err) {
    console.error('Error:', err);
    process.exit(1);
  }
})();
