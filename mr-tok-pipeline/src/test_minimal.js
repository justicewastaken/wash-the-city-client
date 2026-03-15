const { loadImage, createCanvas } = require('canvas');
const fs = require('fs');

(async () => {
  try {
    console.log('Loading image...');
    const img = await loadImage('output/base_image.jpg');
    console.log('Loaded, size:', img.width, img.height);
    const canvas = createCanvas(img.width, img.height);
    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0);
    const buf = canvas.toBuffer('image/png');
    fs.writeFileSync('output/minimal_copy.png', buf);
    console.log('Saved minimal_copy.png');
    process.exit(0);
  } catch (e) {
    console.error('Error:', e);
    process.exit(1);
  }
})();
