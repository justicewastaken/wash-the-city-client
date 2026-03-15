const fs = require('fs');
const path = require('path');
const { createCanvas, loadImage, registerFont } = require('canvas');
const emoji = require('emoji-datasource-apple');

const OUTPUT_DIR = path.join(__dirname, 'output');
const FONT_PATH = path.join(__dirname, '..', 'fonts', 'Montserrat-SemiBold.ttf');
registerFont(FONT_PATH, { family: 'Montserrat', weight: 'semi-bold' });

function renderEmoji(ctx, emojiChar, x, y, fontSize) {
  // Simple: draw emoji as text; canvas supports basic emoji if font has them
  ctx.fillStyle = '#FFFFFF';
  ctx.fillText(emojiChar, x, y);
}

function drawTextWithStroke(ctx, text, x, y, maxWidth, lineHeight, fontSize = 48, strokeColor = '#000000', fillColor = '#FFFFFF', strokeWidth = 3) {
  ctx.font = `${fontSize}px Montserrat`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.lineJoin = 'round';

  const words = text.split(' ');
  let lines = [];
  let currentLine = words[0];

  for (let i = 1; i < words.length; i++) {
    const testLine = currentLine + ' ' + words[i];
    const metrics = ctx.measureText(testLine);
    if (metrics.width > maxWidth && i > 0) {
      lines.push(currentLine);
      currentLine = words[i];
    } else {
      currentLine = testLine;
    }
  }
  lines.push(currentLine);

  // Draw each line with stroke and fill
  lines.forEach((line, index) => {
    const lineY = y - ((lines.length - 1) * lineHeight / 2) + (index * lineHeight);
    // stroke
    ctx.strokeStyle = strokeColor;
    ctx.lineWidth = strokeWidth;
    ctx.strokeText(line, x, lineY);
    // fill
    ctx.fillStyle = fillColor;
    ctx.fillText(line, x, lineY);
  });
}

function addTextOverlay(inputPath, outputPath, topText, bottomText) {
  const image = loadImage(inputPath);
  const canvas = createCanvas(image.width, image.height);
  const ctx = canvas.getContext('2d');

  // Draw original image
  ctx.drawImage(image, 0, 0);

  const padding = 60;
  const maxWidth = image.width - padding * 2;
  const lineHeight = 60;
  const fontSize = 52;

  // Top text (hook)
  if (topText) {
    const topY = padding + lineHeight / 2 + 20;
    drawTextWithStroke(ctx, topText, image.width / 2, topY, maxWidth, lineHeight, fontSize);
  }

  // Bottom text (product/CTA)
  if (bottomText) {
    const bottomY = image.height - padding - lineHeight / 2 - 20;
    drawTextWithStroke(ctx, bottomText, image.width / 2, bottomY, maxWidth, lineHeight, fontSize);
  }

  // Save
  const buffer = canvas.toBuffer('jpg');
  fs.writeFileSync(outputPath, buffer);
  console.log(`Overlay added: ${outputPath}`);
}

// Example usage: node overlay.js <input_image> <output_image> "<top>" "<bottom>"
if (require.main === module) {
  const [,, inputImg, outputImg, topText, bottomText] = process.argv;
  if (!inputImg || !outputImg) {
    console.error('Usage: node overlay.js <input> <output> "<top>" "<bottom>"');
    process.exit(1);
  }
  addTextOverlay(inputImg, outputImg, topText || '', bottomText || '');
}

module.exports = { addTextOverlay };
