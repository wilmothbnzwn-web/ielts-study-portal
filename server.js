const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3456;
const ROOT_DIR = __dirname;
const PUBLIC_DIR = path.join(__dirname, 'public');
const DATA_DIR = path.join(__dirname, 'data');

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
};

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const pathname = url.pathname;

  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');

  // API routes
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
  console.log(`    Home:        http://localhost:${PORT}/`);
  console.log(`    Writing:     http://localhost:${PORT}/writing.html`);
  console.log(`    Reading:     http://localhost:${PORT}/reading.html`);
  console.log(`    Vocabulary:  http://localhost:${PORT}/vocabulary.html`);
  console.log('');
  console.log('  API Endpoints:');
  Object.keys(API_ROUTES).forEach(route => {
    console.log(`    ${route}`);
  });
  console.log('');
  console.log('  Press Ctrl+C to stop');
  console.log('');
});
