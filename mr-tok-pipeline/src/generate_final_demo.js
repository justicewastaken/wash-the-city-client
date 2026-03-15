const { createCanvas, loadImage } = require('canvas');
const fs = require('fs');
const path = require('path');

const inputPath = path.join(process.cwd(), 'output', 'base_image.jpg');
const outputPath = path.join(process.cwd(), 'output', 'final_demo.png');
const topText = 'When your dog asks for a second date 😂';
const bottomText = 'PupJewelry.com • Link in bio';

(async () => {
  try {
    console.log('Loading image from', inputPath);
    const img = await loadImage(inputPath);
    console.log('Image loaded, dimensions:', img.width, img.height);

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

    console.log('Drawing top text');
    drawText(topText, padding + lineHeight / 2 + 20);
    console.log('Drawing bottom text');
    drawText(bottomText, img.height - padding - lineHeight / 2 - 20);

    console.log('Buffering image');
    const buf = canvas.toBuffer('image/png');
    fs.writeFileSync(outputPath, buf);
    console.log('Saved final demo slide:', outputPath);
    console.log('File size:', buf.length);
    process.exit(0);
  } catch (e) {
    console.error('Error:', e);
    process.exit(1);
  }
})();
