const { createCanvas, loadImage } = require('canvas');
const fs = require('fs');

const inputPath = 'output/base_image.jpg';
const outputPath = 'output/demo_slide.png';
const topText = 'When your dog asks for a second date 😂';
const bottomText = 'PupJewelry.com • Link in bio';

(async () => {
  try {
    const img = await loadImage(inputPath);
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

    drawText(topText, padding + lineHeight / 2 + 20);
    drawText(bottomText, img.height - padding - lineHeight / 2 - 20);

    const buf = canvas.toBuffer('image/png');
    fs.writeFileSync(outputPath, buf);
    console.log('Saved demo slide:', outputPath);
    process.exit(0);
  } catch (e) {
    console.error('Overlay error:', e);
    process.exit(1);
  }
})();
