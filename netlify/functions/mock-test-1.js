// Netlify serverless function: mock-test-1
// Serves data/mock-test-1.json — Cambridge IELTS 9 Test 1 mock exam data
const fs = require('fs');
const path = require('path');

exports.handler = async function(event, context) {
  const headers = {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
  };

  try {
    // Use process.cwd() for Lambda environment compatibility (NOT __dirname)
    const dataPath = path.join(process.cwd(), 'data', 'mock-test-1.json');
    const data = fs.readFileSync(dataPath, 'utf-8');
    return {
      statusCode: 200,
      headers,
      body: data,
    };
  } catch (err) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: 'Failed to load mock test data' }),
    };
  }
};
