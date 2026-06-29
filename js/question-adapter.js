/**
 * IELTS Study Portal — Unified Question Adapter Layer
 *
 * Provides a canonical question model so pages don't hardcode
 * different JSON structures for reading vs vocabulary.
 *
 * Canonical Question Model:
 *   id              — string, unique within its type
 *   questionType    — 'reading' | 'vocabulary'
 *   skill           — 'reading' | 'listening' | 'writing' | 'speaking' | 'vocabulary'
 *   questionSubType — e.g. 'true_false_not_given', 'matching', 'choice', 'completion', 'short_answer', 'vocab_flashcard'
 *   title           — short label for lists/cards
 *   stem            — the question text / prompt
 *   options         — array of { label, text } (empty for vocab)
 *   answer          — correct answer(s), string or string[]
 *   explanation     — answer explanation (if available)
 *   source          — { testId, testTitle, topic, examType }
 *   tags            — string[] (topic tags, difficulty, etc.)
 *   estimatedTime   — seconds (if available)
 *   difficulty      — 1-5 (if available)
 *   payload         — original data for detailed rendering
 */

// ── Canonical model factory ─────────────────────────────────────────

/**
 * Create a canonical question object.
 * All fields optional except id, questionType, skill.
 */
export function createQuestion(fields) {
  return {
    id: fields.id || '',
    questionType: fields.questionType || 'reading',     // 'reading' | 'vocabulary'
    skill: fields.skill || 'reading',                    // 'reading' | 'listening' | 'writing' | 'speaking' | 'vocabulary'
    questionSubType: fields.questionSubType || '',        // T/F/NG, matching, choice, completion, short_answer, vocab_flashcard
    title: fields.title || '',
    stem: fields.stem || '',
    options: fields.options || [],
    answer: fields.answer || '',
    explanation: fields.explanation || '',
    source: {
      testId: (fields.source && fields.source.testId) || '',
      testTitle: (fields.source && fields.source.testTitle) || '',
      topic: (fields.source && fields.source.topic) || '',
      examType: (fields.source && fields.source.examType) || '',  // 'Academic' | 'General Training'
    },
    tags: fields.tags || [],
    estimatedTime: fields.estimatedTime || 0,
    difficulty: fields.difficulty || 0,
    payload: fields.payload || {},
  };
}

// ── Reading question adapter ────────────────────────────────────────

/**
 * Question type mapping: reading_tests.json raw type → canonical subType
 */
const READING_TYPE_MAP = {
  'true_false_not_given': 'true_false_not_given',
  'IDENTIFYING': 'true_false_not_given',
  'short_answer': 'short_answer',
  'COMPLETION': 'completion',
  'MATCHING': 'matching',
  'CHOICE': 'choice',
};

/**
 * Human-readable label for question subtype.
 */
export function questionTypeLabel(subType) {
  const labels = {
    'true_false_not_given': '判断题',
    'identifying': '判断题',
    'short_answer': '简答题',
    'completion': '填空题',
    'matching': '匹配题',
    'choice': '单选题',
    'vocab_flashcard': '词汇闪卡',
  };
  return labels[subType] || subType || '';
}

/**
 * Icon for question subtype.
 */
export function questionTypeIcon(subType) {
  const icons = {
    'true_false_not_given': '✓✗',
    'identifying': '✓✗',
    'short_answer': '✏️',
    'completion': '⬜',
    'matching': '🔗',
    'choice': '🔘',
    'vocab_flashcard': '📝',
  };
  return icons[subType] || '❓';
}

/**
 * Skill display info.
 */
export function skillInfo(skill) {
  const map = {
    'reading':    { icon: '📖', label: '阅读', color: 'emerald' },
    'listening':  { icon: '🎧', label: '听力', color: 'blue' },
    'writing':    { icon: '✍️', label: '写作', color: 'purple' },
    'speaking':   { icon: '🎤', label: '口语', color: 'orange' },
    'vocabulary': { icon: '📝', label: '词汇', color: 'amber' },
  };
  return map[skill] || { icon: '📋', label: skill, color: 'brand' };
}

/**
 * Adapt a single reading test question to the canonical model.
 * @param {Object} rawQ — raw question from reading_tests.json
 * @param {Object} testMeta — { id, title, topic, source }
 * @returns {Object} canonical question
 */
export function adaptReadingQuestion(rawQ, testMeta) {
  const rawType = (rawQ.type || rawQ.legacyType || '').toUpperCase();
  const subType = READING_TYPE_MAP[rawType] || rawType.toLowerCase();
  const stem = rawQ.questionText || rawQ.text || '';

  // Build options for T/F/NG and choice questions
  let options = [];
  if (rawType === 'IDENTIFYING' || rawType === 'true_false_not_given') {
    options = [
      { label: 'TRUE', text: 'TRUE' },
      { label: 'FALSE', text: 'FALSE' },
      { label: 'NOT GIVEN', text: 'NOT GIVEN' },
    ];
  } else if ((rawType === 'CHOICE' || rawType === 'MATCHING') && rawQ.options) {
    options = rawQ.options.map((opt, i) => ({
      label: String.fromCharCode(65 + i),  // A, B, C, D...
      text: opt,
    }));
  }

  const answer = rawQ.correctAnswer || rawQ.answerText || '';

  return createQuestion({
    id: String(rawQ.id || ''),
    questionType: 'reading',
    skill: 'reading',
    questionSubType: subType,
    title: stem.substring(0, 60) + (stem.length > 60 ? '…' : ''),
    stem,
    options,
    answer,
    explanation: rawQ.explanation || '',
    source: {
      testId: (testMeta && testMeta.id) || '',
      testTitle: (testMeta && testMeta.title) || '',
      topic: (testMeta && testMeta.topic) || '',
      examType: (testMeta && testMeta.examType) || 'Academic',
    },
    tags: [
      subType,
      (testMeta && testMeta.topic) || '',
    ].filter(Boolean),
    estimatedTime: rawQ.estimatedTime || 90,
    difficulty: (testMeta && testMeta.difficulty) || 0,
    payload: {
      rawQuestion: rawQ,
      testMeta: testMeta || {},
    },
  });
}

/**
 * Adapt a test entry (from reading_tests.json) to a summary object
 * suitable for listing in the library.
 * @param {Object} test — raw test entry
 * @returns {Object} test summary
 */
export function adaptReadingTestSummary(test) {
  // Collect all question subtypes
  const subTypes = new Set();
  (test.questions || []).forEach(q => {
    const rawType = (q.type || q.legacyType || '').toUpperCase();
    const st = READING_TYPE_MAP[rawType] || rawType.toLowerCase();
    subTypes.add(st);
  });

  return {
    id: test.id || '',
    title: test.title || '',
    topic: test.topic || '',
    source: test.source || '',
    difficulty: test.difficulty || 0,
    totalTime: test.totalTime || 3600,
    wordCount: test.wordCount || 0,
    questionCount: test.questionCount || (test.questions || []).length,
    subTypes: Array.from(subTypes),
    mainClass: test.main_class || '',
    estimatedTime: test.totalTime || 3600,
    // Summary of first question as preview
    previewStem: (test.questions && test.questions[0] && test.questions[0].questionText)
      ? test.questions[0].questionText.substring(0, 100)
      : '',
  };
}

// ── Vocabulary question adapter ────────────────────────────────────

/**
 * Adapt a vocabulary word to the canonical question model.
 * @param {Object} rawWord — raw word from vocabulary.json
 * @param {Object} deckMeta — { deckId, deckTitle }
 * @returns {Object} canonical question
 */
export function adaptVocabQuestion(rawWord, deckMeta) {
  const word = rawWord.word || '';
  const chinese = rawWord.chinese || '';

  return createQuestion({
    id: String(rawWord.id || rawWord.word || ''),
    questionType: 'vocabulary',
    skill: 'vocabulary',
    questionSubType: 'vocab_flashcard',
    title: word + (chinese ? ' — ' + chinese : ''),
    stem: word,
    options: [],
    answer: chinese,
    explanation: rawWord.definition || '',
    source: {
      testId: (deckMeta && deckMeta.deckId) || '',
      testTitle: (deckMeta && deckMeta.deckTitle) || rawWord.source || '',
      topic: rawWord.theme || '',
      examType: '',
    },
    tags: [
      'vocabulary',
      rawWord.theme || '',
      rawWord.pos || '',
    ].filter(Boolean),
    estimatedTime: 0,
    difficulty: rawWord.difficulty || 0,
    payload: {
      rawWord,
      deckMeta: deckMeta || {},
    },
  });
}

// ── Mistake book payload → canonical question adapter ──────────────

/**
 * Convert a mistake-book item (from wrong_questions DB) to canonical question.
 * This uses the question_payload JSONB field that was stored at insertion time.
 * @param {Object} dbItem — mapped from wrong_questions row (camelCase)
 * @returns {Object} canonical question
 */
export function adaptMistakeBookItem(dbItem) {
  const payload = dbItem.questionPayload || {};
  const qtype = dbItem.questionType || 'reading';

  if (qtype === 'vocabulary') {
    return createQuestion({
      id: String(dbItem.questionId || ''),
      questionType: 'vocabulary',
      skill: 'vocabulary',
      questionSubType: 'vocab_flashcard',
      title: (payload.word || '') + ((payload.chinese) ? ' — ' + payload.chinese : ''),
      stem: payload.word || '',
      answer: payload.chinese || '',
      explanation: payload.definition || '',
      source: {
        testId: dbItem.sourceExamId || '',
        testTitle: (payload.source) || '',
        topic: payload.theme || '',
        examType: '',
      },
      tags: ['vocabulary', payload.theme || '', payload.pos || ''].filter(Boolean),
      estimatedTime: 0,
      difficulty: payload.difficulty || 0,
      payload,
    });
  }

  // Reading question
  return createQuestion({
    id: String(dbItem.questionId || ''),
    questionType: 'reading',
    skill: 'reading',
    questionSubType: payload.type || '',
    title: (payload.questionText || '').substring(0, 80),
    stem: payload.questionText || '',
    options: [],
    answer: payload.correctAnswer || '',
    explanation: '',
    source: {
      testId: dbItem.sourceExamId || '',
      testTitle: payload.testTitle || '',
      topic: payload.topic || '',
      examType: 'Academic',
    },
    tags: [payload.type || '', payload.topic || ''].filter(Boolean),
    difficulty: 0,
    payload,
  });
}

// ── Utility: renderer helpers ───────────────────────────────────────

/**
 * Get CSS classes for rendering badges.
 */
export function questionTypeBadgeClass(subType) {
  const map = {
    'true_false_not_given': 'bg-amber-50 text-amber-700 border-amber-200',
    'identifying': 'bg-amber-50 text-amber-700 border-amber-200',
    'short_answer': 'bg-blue-50 text-blue-700 border-blue-200',
    'completion': 'bg-indigo-50 text-indigo-700 border-indigo-200',
    'matching': 'bg-purple-50 text-purple-700 border-purple-200',
    'choice': 'bg-cyan-50 text-cyan-700 border-cyan-200',
    'vocab_flashcard': 'bg-pink-50 text-pink-700 border-pink-200',
  };
  return map[subType] || 'bg-brand-50 text-brand-600 border-brand-200';
}

export function skillColorClasses(skill) {
  const map = {
    'reading':    { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', hover: 'hover:bg-emerald-100' },
    'listening':  { bg: 'bg-blue-50',    text: 'text-blue-700',    border: 'border-blue-200',    hover: 'hover:bg-blue-100' },
    'writing':    { bg: 'bg-purple-50',  text: 'text-purple-700',  border: 'border-purple-200',  hover: 'hover:bg-purple-100' },
    'speaking':   { bg: 'bg-orange-50',  text: 'text-orange-700',  border: 'border-orange-200',  hover: 'hover:bg-orange-100' },
    'vocabulary': { bg: 'bg-amber-50',   text: 'text-amber-700',   border: 'border-amber-200',   hover: 'hover:bg-amber-100' },
  };
  return map[skill] || map['reading'];
}

// Make available for non-module scripts as well
if (typeof window !== 'undefined') {
  window._questionAdapter = {
    createQuestion,
    adaptReadingQuestion,
    adaptReadingTestSummary,
    adaptVocabQuestion,
    adaptMistakeBookItem,
    questionTypeLabel,
    questionTypeIcon,
    skillInfo,
    questionTypeBadgeClass,
    skillColorClasses,
  };
}
