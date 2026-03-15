const fs = require('fs');
const { PNG } = require('pngjs');

function createSolidColor(width, height, hexColor) {
  const r = parseInt(hexColor.slice(0, 2), 16);
  const g = parseInt(hexColor.slice(2, 4), 16);
  const b = parseInt(hexColor.slice(4, 6), 16);
  const png = new PNG({ width, height });
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const idx = (width * y + x) << 2;
      png.data[idx] = r;
      png.data[idx + 1] = g;
      png.data[idx + 2] = b;
      png.data[idx + 3] = 255;
    }
  }
  return png;
}

const slides = [
  { color: "4A90E2", text: "When your dog asks for a second date 😂" },
  { color: "9B59B6", text: "The audacity of this man" },
  { color: "2ECC71", text: "Sir, my dog lives here. You are the guest." },
  { color: "E67E22", text: "PupJewelry.com — Personalized pet accessories" },
  { color: "E91E63", text: "Handcrafted, custom name jewelry for your furry friend" },
  { color: "E74C3C", text: "PupJewelry.com • Link in bio" }
];

const width = 1024;
const height = 1024;

slides.forEach((slide, i) => {
  try {
    const png = createSolidColor(width, height, slide.color);
    const outPath = `output/slide_${i+1}_bg.png`;
    const buf = PNG.sync.write(png);
    fs.writeFileSync(outPath, buf);
    console.log(`Created ${outPath}, size ${buf.length}`);
  } catch (e) {
    console.error(`Failed slide ${i+1}:`, e.message);
  }
});

console.log('Done.');
