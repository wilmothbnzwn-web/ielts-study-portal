/**
 * IELTS Study Portal — Database Layer (Supabase)
 *
 * Replaces all localStorage operations with Supabase-backed CRUD.
 * Function names mirror the old localStorage helpers so migration
 * is straightforward: getMyWords, saveMyWords, deleteWord, etc.
 *
 * All functions are async — callers must use await.
 *
 * Column mapping (JS camelCase ↔ DB snake_case):
 *   audioUrl      ↔ audio_url
 *   contextSentence ↔ context_sentence
 *   highFreqWords ↔ high_freq_words
 *   savedAt       ↔ saved_at
 */

import { supabase, authStore } from './auth-store.js';

// ── Helpers ──────────────────────────────────────────────────────

function requireUser() {
  const user = authStore.user;
  if (!user) throw new Error('Not authenticated');
  return user;
}

/** Map a DB row (snake_case) → JS word object (camelCase) */
function mapWordRow(row) {
  return {
    id: row.id,
    word: row.word,
    chinese: row.chinese || '',
    phonetic: row.phonetic || '',
    audioUrl: row.audio_url || '',
    synonyms: parseJsonField(row.synonyms, []),
    contextSentence: row.context_sentence || '',
    savedAt: row.saved_at ? new Date(row.saved_at).getTime() : Date.now(),
  };
}

/** Map a DB row (snake_case) → JS sentence object (camelCase) */
function mapSentenceRow(row) {
  return {
    id: row.id,
    sentence: row.sentence,
    chinese: row.chinese || '',
    highFreqWords: parseJsonField(row.high_freq_words, []),
    savedAt: row.saved_at ? new Date(row.saved_at).getTime() : Date.now(),
  };
}

/** Safely parse a JSON field — returns defaultValue on any failure */
function parseJsonField(value, defaultValue) {
  if (!value) return defaultValue;
  // If already an array/object (Supabase JS client may auto-parse JSONB),
  // return as-is; otherwise try JSON.parse
  if (typeof value === 'object') return value;
  try { return JSON.parse(value); } catch (e) { return defaultValue; }
}

/** Serialize a value for storage in a TEXT column */
function serializeJsonField(value) {
  if (value == null) return '';
  if (typeof value === 'string') return value;
  return JSON.stringify(value);
}

// ── Words ────────────────────────────────────────────────────────

/**
 * Get all words for the current user, newest first.
 * @returns {Promise<Array>}
 */
export async function getMyWords() {
  try {
    const user = requireUser();
    const { data, error } = await supabase
      .from('user_words')
      .select('*')
      .eq('user_id', user.id)
      .order('saved_at', { ascending: false })
      .limit(100);

    if (error) { console.error('getMyWords error:', error); return []; }
    return (data || []).map(mapWordRow);
  } catch (e) {
    console.error('getMyWords exception:', e);
    return [];
  }
}

/**
 * Save word entries to the database. Each word is inserted unless
 * the same word (case-insensitive) already exists for this user.
 * @param {Array} words — array of word entry objects
 */
export async function saveMyWords(words) {
  try {
    const user = requireUser();
    if (!Array.isArray(words) || words.length === 0) return;

    for (const w of words) {
      // Dedup: check if this word already exists for this user
      const { data: existing } = await supabase
        .from('user_words')
        .select('id')
        .eq('user_id', user.id)
        .ilike('word', w.word)
        .maybeSingle();

      if (existing) continue;

      const { error } = await supabase.from('user_words').insert({
        user_id: user.id,
        word: w.word,
        chinese: w.chinese || '',
        phonetic: w.phonetic || '',
        audio_url: w.audioUrl || '',
        synonyms: serializeJsonField(w.synonyms || []),
        context_sentence: w.contextSentence || '',
      });

      if (error) console.error('saveMyWords insert error:', error);
    }
  } catch (e) {
    console.error('saveMyWords exception:', e);
  }
}

/**
 * Delete a word by its UUID.
 * @param {string|number} id — the word's database UUID
 */
export async function deleteWord(id) {
  try {
    requireUser();
    const { error } = await supabase
      .from('user_words')
      .delete()
      .eq('id', id);

    if (error) console.error('deleteWord error:', error);
    return !error;
  } catch (e) {
    console.error('deleteWord exception:', e);
    return false;
  }
}

// ── Sentences ────────────────────────────────────────────────────

/**
 * Get all sentences for the current user, newest first.
 * @returns {Promise<Array>}
 */
export async function getMySentences() {
  try {
    const user = requireUser();
    const { data, error } = await supabase
      .from('user_sentences')
      .select('*')
      .eq('user_id', user.id)
      .order('saved_at', { ascending: false })
      .limit(100);

    if (error) { console.error('getMySentences error:', error); return []; }
    return (data || []).map(mapSentenceRow);
  } catch (e) {
    console.error('getMySentences exception:', e);
    return [];
  }
}

/**
 * Save sentence entries to the database. Each sentence is inserted
 * unless the same sentence already exists for this user.
 * @param {Array} sentences — array of sentence entry objects
 */
export async function saveMySentences(sentences) {
  try {
    const user = requireUser();
    if (!Array.isArray(sentences) || sentences.length === 0) return;

    for (const s of sentences) {
      // Dedup: check if this sentence already exists for this user
      const { data: existing } = await supabase
        .from('user_sentences')
        .select('id')
        .eq('user_id', user.id)
        .ilike('sentence', s.sentence)
        .maybeSingle();

      if (existing) continue;

      const { error } = await supabase.from('user_sentences').insert({
        user_id: user.id,
        sentence: s.sentence,
        chinese: s.chinese || '',
        high_freq_words: serializeJsonField(s.highFreqWords || []),
      });

      if (error) console.error('saveMySentences insert error:', error);
    }
  } catch (e) {
    console.error('saveMySentences exception:', e);
  }
}

/**
 * Delete a sentence by its UUID.
 * @param {string|number} id — the sentence's database UUID
 */
export async function deleteSentence(id) {
  try {
    requireUser();
    const { error } = await supabase
      .from('user_sentences')
      .delete()
      .eq('id', id);

    if (error) console.error('deleteSentence error:', error);
    return !error;
  } catch (e) {
    console.error('deleteSentence exception:', e);
    return false;
  }
}
