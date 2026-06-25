// Vercel serverless function: dictionary API proxy
export default async function handler(req, res) {
  const word = req.query?.word;
  if (!word || !word.trim()) {
    return res.status(400).json({ error: 'Missing word parameter' });
  }

  const cleaned = word.trim().toLowerCase().replace(/[^a-z-]/g, '');
  const apiUrl = `https://api.dictionaryapi.dev/api/v2/entries/en/${encodeURIComponent(cleaned)}`;

  try {
    const apiRes = await fetch(apiUrl, { headers: { 'Accept': 'application/json' } });

    if (apiRes.status === 404) {
      return res.status(200).json({ found: false, word: cleaned });
    }

    const data = await apiRes.json();
    const entry = Array.isArray(data) ? data[0] : data;
    const phonetic = entry.phonetic || entry.phonetics?.find(p => p.text)?.text || '';
    const audioUrl = entry.phonetics?.find(p => p.audio)?.audio || '';
    const synonyms = [];
    if (entry.meanings) {
      entry.meanings.forEach(m => {
        if (m.definitions) {
          m.definitions.forEach(d => { if (d.synonyms) synonyms.push(...d.synonyms); });
        }
        if (m.synonyms) synonyms.push(...m.synonyms);
      });
    }
    const uniqueSynonyms = [...new Set(synonyms)].slice(0, 10);

    return res.status(200).json({
      found: true,
      word: entry.word || cleaned,
      phonetic,
      audioUrl,
      synonyms: uniqueSynonyms,
    });
  } catch (e) {
    return res.status(200).json({ found: false, word: cleaned });
  }
}
