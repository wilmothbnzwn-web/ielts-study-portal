const fs = require('fs');
const path = require('path');

exports.handler = async () => {
  try {
    const data = fs.readFileSync(path.join(process.cwd(), 'data', 'reading-articles.json'), 'utf-8');
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
      },
      body: data,
    };
  } catch (err) {
    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: 'Failed to load reading-articles' }),
    };
  }
};
