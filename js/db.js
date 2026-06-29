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

// ── Mistake Book (Wrong Questions / 错题本) ───────────────────────

/**
 * Map a DB row (snake_case) → JS mistake book item (camelCase)
 */
function mapWrongQuestionRow(row) {
  return {
    id: row.id,
    userId: row.user_id,
    questionId: row.question_id,
    questionType: row.question_type || 'reading',
    questionPayload: parseJsonField(row.question_payload, {}),
    sourceType: row.source_type || 'manual',
    sourceExamId: row.source_exam_id || '',
    wrongCount: row.wrong_count || 0,
    firstAddedAt: row.first_added_at ? new Date(row.first_added_at).getTime() : Date.now(),
    lastWrongAt: row.last_wrong_at ? new Date(row.last_wrong_at).getTime() : Date.now(),
    createdAt: row.created_at ? new Date(row.created_at).getTime() : Date.now(),
    updatedAt: row.updated_at ? new Date(row.updated_at).getTime() : Date.now(),
  };
}

/**
 * Get wrong questions for the current user with pagination.
 * Supports filtering by source_type and question_type.
 *
 * @param {Object} opts — { page?: number, pageSize?: number, sourceType?: string, questionType?: string }
 * @returns {Promise<{ items: Array, total: number, page: number, pageSize: number, hasMore: boolean }>}
 */
export async function getMistakeBookItems(opts = {}) {
  try {
    const user = requireUser();
    const page = Math.max(1, opts.page || 1);
    const pageSize = Math.min(100, Math.max(1, opts.pageSize || 20));
    const from = (page - 1) * pageSize;
    const to = from + pageSize - 1;

    // Build query for items
    let query = supabase
      .from('wrong_questions')
      .select('*', { count: 'exact' })
      .eq('user_id', user.id)
      .order('last_wrong_at', { ascending: false })
      .range(from, to);

    if (opts.sourceType) {
      query = query.eq('source_type', opts.sourceType);
    }
    if (opts.questionType) {
      query = query.eq('question_type', opts.questionType);
    }

    const { data, error, count } = await query;
    if (error) { console.error('getMistakeBookItems error:', error); return { items: [], total: 0, page, pageSize, hasMore: false }; }

    const total = count || 0;
    const hasMore = from + (data || []).length < total;

    return {
      items: (data || []).map(mapWrongQuestionRow),
      total,
      page,
      pageSize,
      hasMore,
    };
  } catch (e) {
    console.error('getMistakeBookItems exception:', e);
    return { items: [], total: 0, page: 1, pageSize: 20, hasMore: false };
  }
}

/**
 * Add a question to the mistake book (upsert).
 * - If the question is NOT yet in the book: inserts a new record.
 * - If the question IS already in the book: increments wrong_count
 *   and updates last_wrong_at.
 *
 * @param {string} questionId     — the question id (from test JSON data or vocab word)
 * @param {string} sourceType     — 'manual' | 'exam' | 'practice'
 * @param {string} [sourceExamId] — optional test/deck id
 * @param {Object} [opts]         — { questionType?: 'reading'|'vocabulary', questionPayload?: object }
 * @returns {Promise<Object|null>} — the upserted record, or null on error
 */
export async function addToMistakeBook(questionId, sourceType = 'manual', sourceExamId = '', opts = {}) {
  try {
    const user = requireUser();
    if (!questionId) return null;

    const questionType = opts.questionType || 'reading';
    const questionPayload = opts.questionPayload || {};

    // Check if this question already exists for this user (by question_id + question_type)
    const { data: existing, error: checkErr } = await supabase
      .from('wrong_questions')
      .select('*')
      .eq('user_id', user.id)
      .eq('question_id', String(questionId))
      .eq('question_type', questionType)
      .maybeSingle();

    if (checkErr) { console.error('addToMistakeBook check error:', checkErr); return null; }

    if (existing) {
      // Update existing record: increment wrong_count, update timestamps
      const newCount = (existing.wrong_count || 0) + 1;
      const updateData = {
        wrong_count: newCount,
        last_wrong_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      // If this is an exam/practice update, update source info
      if ((sourceType === 'exam' || sourceType === 'practice') && sourceExamId) {
        updateData.source_type = sourceType;
        updateData.source_exam_id = String(sourceExamId);
      }
      // Update payload if new one has more data
      if (questionPayload && Object.keys(questionPayload).length > 0) {
        updateData.question_payload = questionPayload;
      }

      const { data: updated, error: updateErr } = await supabase
        .from('wrong_questions')
        .update(updateData)
        .eq('id', existing.id)
        .select('*')
        .single();

      if (updateErr) { console.error('addToMistakeBook update error:', updateErr); return null; }
      return mapWrongQuestionRow(updated);
    }

    // Insert new record
    const { data: inserted, error: insertErr } = await supabase
      .from('wrong_questions')
      .insert({
        user_id: user.id,
        question_id: String(questionId),
        question_type: questionType,
        question_payload: questionPayload,
        source_type: sourceType,
        source_exam_id: sourceExamId ? String(sourceExamId) : null,
        wrong_count: 1,
        first_added_at: new Date().toISOString(),
        last_wrong_at: new Date().toISOString(),
      })
      .select('*')
      .single();

    if (insertErr) {
      // Handle race condition: unique constraint violation (concurrent insert)
      if (insertErr.code === '23505') {
        const { data: raceRow } = await supabase
          .from('wrong_questions')
          .select('*')
          .eq('user_id', user.id)
          .eq('question_id', String(questionId))
          .eq('question_type', questionType)
          .maybeSingle();
        if (raceRow) {
          const newCount = (raceRow.wrong_count || 0) + 1;
          await supabase
            .from('wrong_questions')
            .update({ wrong_count: newCount, last_wrong_at: new Date().toISOString(), updated_at: new Date().toISOString() })
            .eq('id', raceRow.id);
        }
      }
      console.error('addToMistakeBook insert error:', insertErr);
      return null;
    }
    return mapWrongQuestionRow(inserted);
  } catch (e) {
    console.error('addToMistakeBook exception:', e);
    return null;
  }
}

/**
 * Remove a question from the mistake book by its UUID.
 * @param {string} id — the wrong_questions record UUID
 * @returns {Promise<boolean>}
 */
export async function removeFromMistakeBook(id) {
  try {
    requireUser();
    const { error } = await supabase
      .from('wrong_questions')
      .delete()
      .eq('id', id);

    if (error) console.error('removeFromMistakeBook error:', error);
    return !error;
  } catch (e) {
    console.error('removeFromMistakeBook exception:', e);
    return false;
  }
}

/**
 * Check whether a question is already in the current user's mistake book.
 * Returns the record id if found, or null.
 * @param {string} questionId
 * @param {string} [questionType='reading'] — 'reading' | 'vocabulary'
 * @returns {Promise<string|null>} — the record UUID if found, null otherwise
 */
export async function isInMistakeBook(questionId, questionType = 'reading') {
  try {
    const user = requireUser();
    if (!questionId) return null;

    let query = supabase
      .from('wrong_questions')
      .select('id')
      .eq('user_id', user.id)
      .eq('question_id', String(questionId));

    if (questionType) {
      query = query.eq('question_type', questionType);
    }

    const { data, error } = await query.maybeSingle();

    if (error) { console.error('isInMistakeBook error:', error); return null; }
    return data ? data.id : null;
  } catch (e) {
    console.error('isInMistakeBook exception:', e);
    return null;
  }
}

