// Vercel serverless function: MyMemory translation proxy
export default async function handler(req, res) {
  const rawText = req.query?.text;
  if (!rawText || !rawText.trim()) {
    return res.status(400).json({ error: 'Missing text parameter' });
  }

  const cleaned = rawText.replace(/[\n\r]+/g, ' ').replace(/\s+/g, ' ').trim();
  const apiUrl = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(cleaned)}&langpair=en|zh`;

  try {
    const apiRes = await fetch(apiUrl);
    const data = await apiRes.json();
    return res.status(200).json({
      translatedText: data.responseData?.translatedText || cleaned,
      match: data.responseData?.match || 0,
      source: 'MyMemory API',
    });
  } catch (e) {
    return res.status(502).json({ error: 'Translation service unavailable' });
  }
}
