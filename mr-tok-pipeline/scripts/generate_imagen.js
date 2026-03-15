const { GoogleAuth } = require('google-auth-library');
const axios = require('axios');
const fs = require('fs');

const PROJECT = 'lisa-490020';
const LOC = 'us-central1';
const MODEL = 'imagegeneration@001';
const SA_KEY = '/root/.openclaw/workspace/gemini_service_account.json';

async function getToken() {
  const auth = new GoogleAuth({ keyFile: SA_KEY, scopes: ['https://www.googleapis.com/auth/cloud-platform'] });
  const client = await auth.getClient();
  const token = await client.getAccessToken();
  return token.token;
}

async function generateImage(prompt) {
  const token = await getToken();
  const url = `https://${LOC}-aiplatform.googleapis.com/v1/projects/${PROJECT}/locations/${LOC}/publishers/google/models/${MODEL}:predict`;
  const payload = {
    instances: [{ prompt }],
    parameters: { sampleCount: 1, style: "enhanced" }
  };
  try {
    const res = await axios.post(url, payload, {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      timeout: 120000
    });
    return res.data.predictions[0]; // base64 string
  } catch (err) {
    console.error('Imagen error:', err.response?.status, err.response?.data || err.message);
    throw err;
  }
}

// Test
generateImage('A candid iPhone photo of a golden retriever on couch, warm lighting')
  .then(b64 => {
    const buf = Buffer.from(b64, 'base64');
    fs.writeFileSync('output/test_imagen.png', buf);
    console.log('Saved test_imagen.png');
  })
  .catch(e => process.exit(1));
