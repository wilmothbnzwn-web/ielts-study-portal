/**
 * Netlify Function: /js/env.js
 * Injects Supabase environment variables into the browser as an ES module.
 * Called via rewrite rule: /js/env.js → /.netlify/functions/env
 */
exports.handler = async function () {
  const SUPABASE_URL = process.env.SUPABASE_URL || '';
  const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY || '';

  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/javascript; charset=utf-8',
      'Cache-Control': 'no-cache',
    },
    body: `export const SUPABASE_URL = ${JSON.stringify(SUPABASE_URL)};
export const SUPABASE_ANON_KEY = ${JSON.stringify(SUPABASE_ANON_KEY)};
`,
  };
};
