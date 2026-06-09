const https = require('https');

exports.handler = async (event) => {
  const word = event.queryStringParameters?.word;
  if (!word || !word.trim()) {
    return {
      statusCode: 400,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
      },
      body: JSON.stringify({ error: 'Missing word parameter' }),
    };
  }

  const cleaned = word.trim().toLowerCase().replace(/[^a-z-]/g, '');
  const apiUrl = `https://api.dictionaryapi.dev/api/v2/entries/en/${encodeURIComponent(cleaned)}`;

  return new Promise((resolve) => {
    https.get(apiUrl, { headers: { 'Accept': 'application/json' } }, (apiRes) => {
      let body = '';
      apiRes.on('data', chunk => body += chunk);
      apiRes.on('end', () => {
        if (apiRes.statusCode === 404) {
          resolve({
            statusCode: 200,
            headers: { 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify({ found: false, word: cleaned }),
          });
          return;
        }
        try {
          const data = JSON.parse(body);
          const entry = Array.isArray(data) ? data[0] : data;
          const phonetic = entry.phonetic || entry.phonetics?.find(p => p.text)?.text || '';
          const audioUrl = entry.phonetics?.find(p => p.audio)?.audio || '';
          const synonyms = [];
          if (entry.meanings) {
            entry.meanings.forEach(m => {
              if (m.definitions) {
                m.definitions.forEach(d => {
                  if (d.synonyms) synonyms.push(...d.synonyms);
                });
              }
              if (m.synonyms) synonyms.push(...m.synonyms);
            });
          }
          const uniqueSynonyms = [...new Set(synonyms)].slice(0, 10);
          resolve({
            statusCode: 200,
            headers: { 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify({
              found: true,
              word: entry.word || cleaned,
              phonetic: phonetic,
              audioUrl: audioUrl,
              synonyms: uniqueSynonyms,
            }),
          });
        } catch (e) {
          resolve({
            statusCode: 200,
            headers: { 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify({ found: false, word: cleaned }),
          });
        }
      });
    }).on('error', () => {
      resolve({
        statusCode: 200,
        headers: { 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*' },
        body: JSON.stringify({ found: false, word: cleaned }),
      });
    });
  });
};
