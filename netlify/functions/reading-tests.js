// Netlify serverless function: reading-tests
// Serves data/reading_tests.json — reading test library with 3 mock exams
const fs = require('fs');
const path = require('path');

exports.handler = async function(event, context) {
  const headers = {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
  };

  try {
    const dataPath = path.join(process.cwd(), 'data', 'reading_tests.json');
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
      body: JSON.stringify({ error: 'Failed to load reading tests data' }),
    };
  }
};
