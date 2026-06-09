const fs = require('fs');
const path = require('path');

module.exports = (req, res) => {
  try {
    const data = fs.readFileSync(path.join(process.cwd(), 'data', 'vocabulary.json'), 'utf-8');
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET');
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.statusCode = 200;
    res.end(data);
  } catch (err) {
    res.statusCode = 500;
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({ error: 'Failed to load vocabulary' }));
  }
};
