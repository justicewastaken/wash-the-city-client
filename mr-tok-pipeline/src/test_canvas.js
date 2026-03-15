const { createCanvas, loadImage } = require('canvas');
const fs = require('fs');

(async () => {
  const img = await loadImage('output/cat.jpg');
  const canvas = createCanvas(img.width, img.height);
  const ctx = canvas.getContext('2d');
  ctx.drawImage(img, 0, 0);
  const buf = canvas.toBuffer('image/png');
  console.log('buffer length', buf.length);
  fs.writeFileSync('output/test_canvas.png', buf);
  console.log('saved test_canvas.png');
})().catch(e => console.error(e));
