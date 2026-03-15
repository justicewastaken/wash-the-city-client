const { createCanvas } = require('canvas');
const fs = require('fs');

const width = 1024;
const height = 1024;
const canvas = createCanvas(width, height);
const ctx = canvas.getContext('2d');

// Solid warm background (beige)
ctx.fillStyle = '#F5F5DC';
ctx.fillRect(0, 0, width, height);

// Text styling
const padding = 60;
const maxWidth = width - padding * 2;
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
    ctx.strokeText(l, width / 2, yPos);
    ctx.fillText(l, width / 2, yPos);
  });
}

drawText('When your dog asks for a second date 😂', padding + lineHeight / 2 + 20);
drawText('PupJewelry.com • Link in bio', height - padding - lineHeight / 2 - 20);

const outPath = 'output/solid_slide.png';
fs.writeFileSync(outPath, canvas.toBuffer('image/png'));
console.log('Created solid slide with overlay:', outPath);
