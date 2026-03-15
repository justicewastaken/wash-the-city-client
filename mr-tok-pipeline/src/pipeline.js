const path = require('path');
const fs = require('fs');
const { generateImage } = require('./generate_image');
const { addTextOverlay } = require('./overlay');

const OUTPUT_DIR = path.join(__dirname, 'output');

// Sample content - in reality, this would come from a skill invocation
const sampleProduct = {
  name: "Personalized Pet Jewelry",
  hook: "When your dog asks for a second date 😂",
  cta: "PupJewelry.com • Link in bio"
};

async function runPipeline(product) {
  // 1. Load scenes and personas
  const scenes = JSON.parse(fs.readFileSync(path.join(__dirname, 'scene_library', 'scene_001.json'), 'utf8'));
  const personas = JSON.parse(fs.readFileSync(path.join(__dirname, 'personas', 'dog_mom.json'), 'utf8'));
  
  // Build prompt using scene + persona
  const prompt = `${personas.camera_roll_style.type.replace(/_/g, ' ')}: ${scenes.prompt_template} product: ${product.name}`;
  console.log('Final prompt:', prompt);

  // 2. Generate base image
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const rawImage = path.join(OUTPUT_DIR, `raw_${timestamp}.jpg`);
  await generateImage(prompt, rawImage);

  // 3. Add text overlay
  const finalImage = path.join(OUTPUT_DIR, `slide_${timestamp}.jpg`);
  addTextOverlay(rawImage, finalImage, product.hook, product.cta);

  // 4. Cleanup raw if desired
  // fs.unlinkSync(rawImage);

  return finalImage;
}

// Test run
runPipeline(sampleProduct).then(path => {
  console.log('Pipeline complete. Final slide:', path);
}).catch(err => {
  console.error('Pipeline failed:', err);
});
