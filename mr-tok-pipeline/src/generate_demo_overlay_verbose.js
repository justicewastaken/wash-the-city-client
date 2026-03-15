const { createCanvas, loadImage } = require('canvas');
const fs = require('fs');

const inputPath = 'output/base_image.jpg';
const outputPath = 'output/demo_slide.png';
const topText = 'When your dog asks for a second date 😂';
const bottomText = 'PupJewelry.com • Link in bio';

(async () => {
  try {
    console.log('Step 1: load image');
    const img = await loadImage(inputPath);
    console.log('Image loaded, dimensions:', img.width, img.height);

    console.log('Step 2: create canvas');
    const canvas = createCanvas(img.width, img.height);
    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0);
    console.log('Drawn image');

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

    console.log('Step 3: draw top text');
    drawText(topText, padding + lineHeight / 2 + 20);
    console.log('Step 4: draw bottom text');
    drawText(bottomText, img.height - padding - lineHeight / 2 - 20);

    console.log('Step 5: buffer and write');
    const buf = canvas.toBuffer('image/png');
    fs.writeFileSync(outputPath, buf);
    console.log('Saved demo slide:', outputPath);
    process.exit(0);
  } catch (e) {
    console.error('Error:', e);
    process.exit(1);
  }
})();
