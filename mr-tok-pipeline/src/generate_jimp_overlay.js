const Jimp = require('jimp');

const imagePath = 'output/base.jpg';
const outputPath = 'output/final_jimp.png';
const topText = 'When your dog asks for a second date 😂';
const bottomText = 'PupJewelry.com • Link in bio';

(async () => {
  try {
    console.log('Reading image...');
    const img = await Jimp.read(imagePath);
    const w = img.getWidth();
    const h = img.getHeight();
    console.log('Image size:', w, h);

    // Load font (we have Montserrat)
    let font;
    try {
      font = await Jimp.loadFont('fonts/Montserrat-SemiBold.ttf');
      console.log('Loaded custom font');
    } catch (e) {
      console.warn('Custom font not found, using built-in');
      font = Jimp.FONT_SANS_32_BLACK; // this includes stroke?
    }

    // Jimp's print doesn't have built-in stroke. We'll simulate by printing black text offset then white.
    function printWithStroke(img, font, text, x, y, fontSize = 52) {
      // We need to measure text to center
      const metrics = Jimp.measureText(font, text);
      const textWidth = metrics.width;
      const textHeight = metrics.height;
      const posX = x - Math.floor(textWidth / 2);
      const posY = y - Math.floor(textHeight / 2);
      // Shadow (black) with slight offset
      img.print(font, posX + 3, posY + 3, text);
      // Fill (white)
      img.print(font, posX, posY, text);
    }

    const topY = 80;
    const bottomY = h - 80;
    const centerX = Math.floor(w / 2);

    console.log('Printing text...');
    printWithStroke(img, font, topText, centerX, topY);
    printWithStroke(img, font, bottomText, centerX, bottomY);

    console.log('Writing output...');
    await img.writeAsync(outputPath);
    console.log('Saved:', outputPath);
    const stats = await Jimp.read(outputPath).then(im => im.getFileInfo());
    console.log('Size:', stats.size);
    process.exit(0);
  } catch (err) {
    console.error('Error:', err);
    process.exit(1);
  }
})();
