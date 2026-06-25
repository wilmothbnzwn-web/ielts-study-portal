// Vercel serverless function: serve Supabase env vars as ES module
export default function handler(req, res) {
  const SUPABASE_URL = process.env.SUPABASE_URL || '';
  const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY || '';
  res.setHeader('Content-Type', 'application/javascript; charset=utf-8');
  res.setHeader('Cache-Control', 'no-cache');
  res.status(200).send(
    `export const SUPABASE_URL = ${JSON.stringify(SUPABASE_URL)};\nexport const SUPABASE_ANON_KEY = ${JSON.stringify(SUPABASE_ANON_KEY)};\n`
  );
}
