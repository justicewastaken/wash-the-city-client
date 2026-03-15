const fs = require('fs');
const path = require('path');
const axios = require('axios');

const SCENE_DIR = path.join(__dirname, '..', 'scene_library');
const PERSONA_DIR = path.join(__dirname, '..', 'personas');
const OUTPUT_DIR = path.join(__dirname, '..', 'output');

// Load all JSON files from a directory
function loadJSON(dir) {
  if (!fs.existsSync(dir)) {
    throw new Error(`Directory not found: ${dir}`);
  }
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.json'));
  return files.map(f => {
    const content = fs.readFileSync(path.join(dir, f), 'utf8');
    return JSON.parse(content);
  });
}

function randomChoice(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function buildPrompt(scene, persona) {
  const scenePrompt = scene.prompt_template ||
    `${scene.camera?.holder || ''} perspective, ${scene.subject?.action || ''} ${scene.subject?.primary || ''}, ${scene.background?.environment || ''}, ${scene.style?.camera_roll_aesthetic || ''}`;
  const personaLens = persona.camera_roll_style?.type?.replace(/_/g, ' ') || persona.name;
  return `From the lens of a ${personaLens}: ${scenePrompt}`;
}

async function generateImage(prompt, outputPath) {
  const encodedPrompt = encodeURIComponent(prompt);
  const url = `https://image.pollinations.ai/prompt/${encodedPrompt}?width=1024&height=1024&nologo=true&seed=${Date.now()}`;
  const response = await axios.get(url, { responseType: 'stream' });
  await new Promise((resolve, reject) => {
    response.data.pipe(fs.createWriteStream(outputPath))
      .on('finish', resolve)
      .on('error', reject);
  });
}

// Standalone generator (for testing)
function main() {
  const scenes = loadJSON(SCENE_DIR);
  const personas = loadJSON(PERSONA_DIR);
  const scene = randomChoice(scenes);
  const persona = randomChoice(personas);
  const prompt = buildPrompt(scene, persona);

  console.log(`Generating image for prompt: ${prompt}`);
  console.log(`Scene: ${scene.name}, Persona: ${persona.name}`);

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `raw_${timestamp}.jpg`;
  const outputPath = path.join(OUTPUT_DIR, filename);

  generateImage(prompt, outputPath)
    .then(() => {
      console.log(`Saved to ${outputPath}`);
      // Save metadata
      const meta = { scene: scene.id, persona: persona.id, prompt, image: filename };
      fs.writeFileSync(path.join(OUTPUT_DIR, `meta_${timestamp}.json`), JSON.stringify(meta, null, 2));
    })
    .catch(err => {
      console.error('Failed to generate image:', err.message);
    });
}

main();

module.exports = { generateImage, buildPrompt, loadJSON, randomChoice };
