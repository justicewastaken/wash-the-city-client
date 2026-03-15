const { GoogleAuth } = require('google-auth-library');
const axios = require('axios');
const fs = require('fs');

const PROJECT_ID = 'lisa-490020';
const LOCATION = 'us-central1';
const MODEL_ID = 'imagegeneration@001'; // Imagen model
const SERVICE_ACCOUNT_FILE = '/root/.openclaw/workspace/gemini_service_account.json';

async function getAccessToken() {
  const { GoogleAuth } = require('google-auth-library');
  const auth = new GoogleAuth({
    keyFile: SERVICE_ACCOUNT_FILE,
    scopes: ['https://www.googleapis.com/auth/cloud-platform'],
  });
  const client = await auth.getClient();
  const token = await client.getAccessToken();
  return token.token;
}

async function generateImage(prompt) {
  const token = await getAccessToken();
  const url = `https://${LOCATION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/publishers/google/models/${MODEL_ID}:predict`;
  const payload = {
    instances: [{ prompt }],
    parameters: {
      sampleCount: 1,
      // Optional: style, etc.
    }
  };
  const response = await axios.post(url, payload, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    timeout: 120000
  });
  // Response contains base64-encoded images
  const predictions = response.data.predictions;
  return predictions; // array of base64 strings
}

// Test
generateImage('A cute dog wearing a necklace, photorealistic, iPhone photo')
  .then(imgs => {
    console.log('Got predictions count:', imgs.length);
    if (imgs[0]) {
      const base64 = imgs[0];
      const buffer = Buffer.from(base64, 'base64');
      fs.writeFileSync('output/imagen_test.png', buffer);
      console.log('Saved imagen_test.png, size:', buffer.length);
    }
  })
  .catch(err => {
    console.error('Error:', err.response?.status, err.response?.data || err.message);
  });
