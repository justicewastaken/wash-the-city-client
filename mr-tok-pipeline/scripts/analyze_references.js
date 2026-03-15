const { GoogleAuth } = require('google-auth-library');
const axios = require('axios');
const fs = require('fs');
const path = require('path');

const PROJECT_ID = 'lisa-490020';
const LOCATION = 'us-central1';
const MODEL_ID = 'gemini-1.5-pro-002';
const SERVICE_ACCOUNT_FILE = '/root/.openclaw/workspace/gemini_service_account.json';

const INPUT_DIR = '/root/.openclaw/media/inbound';
const OUTPUT_DIR = path.join(__dirname, 'analysis');

if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR);

async function getAccessToken() {
  const auth = new GoogleAuth({
    keyFile: SERVICE_ACCOUNT_FILE,
    scopes: ['https://www.googleapis.com/auth/cloud-platform'],
  });
  const client = await auth.getClient();
  const token = await client.getAccessToken();
  return token.token;
}

const ANALYSIS_PROMPT = `You are an expert TikTok slideshow analyst. I will give you an image. Output a JSON object with these fields (only JSON, no markdown):

{
  "scene": {
    "camera_holder": "first_person" | "third_person" | "overhead" | "side_view" | "unknown",
    "camera_height": "eye_level" | "low_angle" | "high_angle" | "unknown",
    "camera_angle": "forward_facing" | "looking_down" | "looking_up" | "profile" | "unknown",
    "subject_primary": "string",
    "subject_action": "string",
    "subject_position": "center_frame" | "rule_of_thirds" | "off_center",
    "background_environment": "string",
    "background_lighting": "natural_light" | "soft_indoor" | "low_light_night" | "studio" | "mixed",
    "style_color_palette": "warm_tones" | "cool_tones" | "neutral" | "vibrant",
    "mood": "cozy" | "funny" | "aspirational" | "raw" | "heartfelt" | "generic"
  },
  "persona": {
    "type": "dog_mom" | "new_parent" | "fitness_enthusiast" | "student" | "professional" | "other",
    "demographics": { "age_range": "18-24" | "25-34" | "35-44" | "45+" | "unknown" },
    "camera_roll_style": "candid_iphone_shots" | "professional_photos" | "social_media_influencer" | "unknown",
    "values": ["value1","value2","value3"]
  },
  "text_overlay": {
    "top_text_present": true,
    "bottom_text_present": true,
    "font_style": "sans_serif" | "serif" | "unknown",
    "font_weight": "bold" | "regular",
    "stroke": "black_outline" | "none" | "unknown",
    "emoji_used": true,
    "position_top_percent": 0.2,
    "position_bottom_percent": 0.8
  },
  "product": {
    "visible": true,
    "type": "pet_jewelry" | "apparel" | "beauty" | "electronics" | "food" | "other",
    "presentation": "flat_lay" | "being_worn" | "in_use" | "static_display"
  }
}`;

async function analyzeImage(imagePath) {
  const token = await getAccessToken();
  const imageBase64 = fs.readFileSync(imagePath).toString('base64');
  const mimeType = 'image/jpeg'; // assume jpg
  const url = `https://${LOCATION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/publishers/google/models/${MODEL_ID}:generateContent`;

  const payload = {
    contents: [
      {
        role: 'user',
        parts: [
          { text: ANALYSIS_PROMPT },
          {
            inlineData: {
              mimeType,
              data: imageBase64
            }
          }
        ]
      }
    ],
    generationConfig: {
      response_mime_type: 'application/json'
    }
  };

  const response = await axios.post(url, payload, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    timeout: 60000
  });

  const text = response.data.candidates[0].content.parts[0].text;
  return JSON.parse(text);
}

async function main() {
  const files = fs.readdirSync(INPUT_DIR).filter(f => /\.(jpg|jpeg|png)$/i.test(f));
  for (const file of files) {
    const fullPath = path.join(INPUT_DIR, file);
    try {
      console.log(`Analyzing ${file}...`);
      const analysis = await analyzeImage(fullPath);
      const outFile = path.join(OUTPUT_DIR, `analysis_${path.basename(file, path.extname(file))}.json`);
      fs.writeFileSync(outFile, JSON.stringify(analysis, null, 2));
      console.log(`Saved analysis to ${outFile}`);
    } catch (err) {
      console.error(`Failed to analyze ${file}:`, err.message);
      if (err.response) {
        console.error('Response status:', err.response.status);
        console.error('Response data:', err.response.data);
      }
    }
  }
}

main().catch(console.error);
