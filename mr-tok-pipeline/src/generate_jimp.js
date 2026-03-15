const Jimp = require('jimp');
const path = require('path');

const inputPath = path.join(process.cwd(), 'output', 'base_image.jpg');
const outputPath = path.join(process.cwd(), 'output', 'final_demo_jimp.png');
const fontPath = path.join(process.cwd(), 'fonts', 'Montserrat-SemiBold.ttf'); // we have this from earlier download

const topText = 'When your dog asks for a second date 😂';
const bottomText = 'PupJewelry.com • Link in bio';

(async () => {
  try {
    console.log('Loading image:', inputPath);
    const image = await Jimp.read(inputPath);
    const width = image.getWidth();
    const height = image.getHeight();
    console.log('Image size:', width, height);

    // Load font (fallback to built-in if not found)
    let font;
    try {
      font = await Jimp.loadFont(fontPath);
      console.log('Loaded custom font:', fontPath);
    } catch (e) {
      console.warn('Custom font not found, using built-in FONT_SANS_32');
      font = Jimp.FONT_SANS_32;
    }

    // Function to print text with stroke (black shadow + white fill)
    function printWithStroke(image, font, text, x, y, fontSize = 48) {
      // Jimp's font's height is based on the loaded font size; we can't easily scale unless we load different size. We'll use font as-is.
      // For stroke, print black with offset then white on top.
      const shadowOffset = 2;
      // We need to center horizontally: measure text width (Jimp doesn't have measureText for custom fonts? Actually it does: Jimp.measureText(font, text) returns { width, height }.
      const metrics = Jimp.measureText(font, text);
      const centeredX = x - Math.floor(metrics.width / 2);
      const centeredY = y - Math.floor(metrics.height / 2);

      // Shadow (black)
      image.print(font, centeredX + shadowOffset, centeredY + shadowOffset, text);
      // Fill (white)
      image.print(font, centeredX, centeredY, text);
    }

    const padding = 60;
    const topY = padding + 50; // near top
    const bottomY = height - padding - 50;

    console.log('Printing top and bottom text');
    printWithStroke(image, font, topText, Math.floor(width / 2), topY);
    printWithStroke(image, font, bottomText, Math.floor(width / 2), bottomY);

    console.log('Writing output to', outputPath);
    await image.writeAsync(outputPath);
    console.log('Final slide created:', outputPath);
    process.exit(0);
  } catch (err) {
    console.error('Error:', err);
    process.exit(1);
  }
})();
