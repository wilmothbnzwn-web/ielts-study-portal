const https = require('https');

exports.handler = async (event) => {
  const rawText = event.queryStringParameters?.text;
  if (!rawText || !rawText.trim()) {
    return {
      statusCode: 400,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
      },
      body: JSON.stringify({ error: 'Missing text parameter' }),
    };
  }

  // Clean text: remove newlines, collapse whitespace
  const cleaned = rawText.replace(/[\n\r]+/g, ' ').replace(/\s+/g, ' ').trim();

  return new Promise((resolve) => {
    const apiUrl = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(cleaned)}&langpair=en|zh`;

    https.get(apiUrl, (apiRes) => {
      let body = '';
      apiRes.on('data', chunk => body += chunk);
      apiRes.on('end', () => {
        try {
          const data = JSON.parse(body);
          resolve({
            statusCode: 200,
            headers: {
              'Content-Type': 'application/json; charset=utf-8',
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Methods': 'GET',
            },
            body: JSON.stringify({
              translatedText: data.responseData?.translatedText || cleaned,
              match: data.responseData?.match || 0,
              source: 'MyMemory API',
            }),
          });
        } catch (e) {
          resolve({
            statusCode: 502,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify({ error: 'Translation service unavailable' }),
          });
        }
      });
    }).on('error', () => {
      resolve({
        statusCode: 502,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        body: JSON.stringify({ error: 'Translation service unreachable' }),
      });
    });
  });
};
