const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');

const PORT = Number(process.env.PORT) || 3456;
const ROOT_DIR = __dirname;
const PUBLIC_DIR = path.join(__dirname, 'public');
const DATA_DIR = path.join(__dirname, 'data');

// ===== Zero-dependency .env.local loader =====
(function loadEnv() {
  const envPath = path.join(__dirname, '.env.local');
  if (!fs.existsSync(envPath)) return;
  const content = fs.readFileSync(envPath, 'utf-8');
  for (const line of content.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eqIdx = trimmed.indexOf('=');
    if (eqIdx === -1) continue;
    const key = trimmed.slice(0, eqIdx).trim();
    let value = trimmed.slice(eqIdx + 1).trim();
    if ((value.startsWith('"') && value.endsWith('"')) ||
        (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    if (!process.env[key]) process.env[key] = value;
  }
  if (process.env.SUPABASE_URL) {
    console.log('  [env] Loaded SUPABASE_URL from .env.local');
  }
})();

// MIME types
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
};

// API route mapping
const API_ROUTES = {
  '/api/band-descriptors': 'band-descriptors.json',
  '/api/vocabulary': 'vocabulary.json',
  '/api/reading-articles': 'reading-articles.json',
  '/api/essays': 'essays.json',
  '/api/methodology': 'methodology.json',
  '/api/dictionary': 'dictionary.json',
  '/api/mock-test-1': 'mock-test-1.json',
  '/api/reading-tests': 'reading_tests.json',
  '/api/general-writing-tasks': 'general_writing_tasks.json',
};

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const pathname = url.pathname;

  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');

  // Dynamic env module — injects Supabase config into browser
  if (pathname === '/js/env.js') {
    res.writeHead(200, { 'Content-Type': 'application/javascript; charset=utf-8' });
    res.end(`export const SUPABASE_URL = ${JSON.stringify(process.env.SUPABASE_URL || '')};
export const SUPABASE_ANON_KEY = ${JSON.stringify(process.env.SUPABASE_ANON_KEY || '')};
`);
    return;
  }

  // API route: translate proxy (backend-forwards to MyMemory, avoids CORS preflight)
  if (pathname === '/api/translate') {
    const rawText = url.searchParams.get('text');
    if (!rawText || !rawText.trim()) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Missing text parameter' }));
      return;
    }
    // Clean text: remove newlines, collapse whitespace
    const cleaned = rawText.replace(/[\n\r]+/g, ' ').replace(/\s+/g, ' ').trim();
    const apiUrl = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(cleaned)}&langpair=en|zh`;

    https.get(apiUrl, (apiRes) => {
      let body = '';
      apiRes.on('data', chunk => body += chunk);
      apiRes.on('end', () => {
        try {
          const data = JSON.parse(body);
          res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
          res.end(JSON.stringify({
            translatedText: data.responseData?.translatedText || cleaned,
            match: data.responseData?.match || 0,
            source: 'MyMemory API',
          }));
        } catch (e) {
          res.writeHead(502, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Translation service unavailable' }));
        }
      });
    }).on('error', (err) => {
      res.writeHead(502, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Translation service unreachable' }));
    });
    return;
  }

  // API route: dictionary lookup proxy (Free Dictionary API)
  if (pathname === '/api/dictionary-lookup') {
    const word = url.searchParams.get('word');
    if (!word || !word.trim()) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Missing word parameter' }));
      return;
    }
    const cleaned = word.trim().toLowerCase().replace(/[^a-z-]/g, '');
    const apiUrl = `https://api.dictionaryapi.dev/api/v2/entries/en/${encodeURIComponent(cleaned)}`;

    https.get(apiUrl, { headers: { 'Accept': 'application/json' } }, (apiRes) => {
      let body = '';
      apiRes.on('data', chunk => body += chunk);
      apiRes.on('end', () => {
        if (apiRes.statusCode === 404) {
          res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
          res.end(JSON.stringify({ found: false, word: cleaned }));
          return;
        }
        try {
          const data = JSON.parse(body);
          // Extract useful fields
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
          res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
          res.end(JSON.stringify({
            found: true,
            word: entry.word || cleaned,
            phonetic: phonetic,
            audioUrl: audioUrl,
            synonyms: uniqueSynonyms,
          }));
        } catch (e) {
          res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
          res.end(JSON.stringify({ found: false, word: cleaned }));
        }
      });
    }).on('error', () => {
      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
      res.end(JSON.stringify({ found: false, word: cleaned }));
    });
    return;
  }

  // API routes (static JSON)
  if (API_ROUTES[pathname]) {
    const filePath = path.join(DATA_DIR, API_ROUTES[pathname]);
    try {
      const data = fs.readFileSync(filePath, 'utf-8');
      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
      res.end(data);
    } catch (err) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Failed to load data' }));
    }
    return;
  }

  // Static files — search root first (Vercel layout), then public/ (legacy)
  let filePath;

  if (pathname === '/') {
    filePath = path.join(ROOT_DIR, 'index.html');
  } else if (pathname === '/vocab' || pathname === '/vocabulary') {
    filePath = path.join(ROOT_DIR, 'vocabulary.html');
  } else if (pathname.startsWith('/vocab/deck/') || pathname.startsWith('/vocabulary/deck/')) {
    filePath = path.join(ROOT_DIR, 'vocab-deck.html');
  } else {
    filePath = path.join(ROOT_DIR, pathname);
  }

  // Try exact path, then .html extension
  if (!fs.existsSync(filePath) && !path.extname(filePath)) {
    const htmlPath = filePath + '.html';
    if (fs.existsSync(htmlPath)) {
      filePath = htmlPath;
    }
  }

  // Fallback: try public/ directory for any remaining static assets
  if (!fs.existsSync(filePath)) {
    const publicPath = path.join(PUBLIC_DIR, pathname.replace(/^\//, ''));
    if (fs.existsSync(publicPath)) {
      filePath = publicPath;
    }
  }

  // Final fallback to root index.html
  if (!fs.existsSync(filePath)) {
    filePath = path.join(ROOT_DIR, 'index.html');
  }

  const ext = path.extname(filePath).toLowerCase();
  const contentType = MIME[ext] || 'application/octet-stream';

  try {
    const content = fs.readFileSync(filePath);
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(content);
  } catch (err) {
    res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end('<h1>404 - Page Not Found</h1>');
  }
});

server.listen(PORT, () => {
  console.log('');
  console.log('  ✦ IELTS Study Portal ✦');
  console.log('  ─────────────────────');
  console.log(`  Server running at:  http://localhost:${PORT}`);
  console.log('');
  console.log('  Pages:');
  console.log(`    Practice:     http://localhost:${PORT}/`);
  console.log(`    Reading:      http://localhost:${PORT}/reading-library.html`);
  console.log(`    Writing:      http://localhost:${PORT}/writing.html`);
  console.log(`    Vocabulary:   http://localhost:${PORT}/vocabulary`);
  console.log(`    Mock Test:    http://localhost:${PORT}/mock-test.html`);
  console.log(`    MistakeBook:  http://localhost:${PORT}/mistake-book.html`);
  console.log(`    Collection:   http://localhost:${PORT}/collection.html`);
  console.log('');
  console.log('  API Endpoints:');
  Object.keys(API_ROUTES).forEach(route => {
    console.log(`    ${route}`);
  });
  console.log('');
  console.log('  Press Ctrl+C to stop');
  console.log('');
});
