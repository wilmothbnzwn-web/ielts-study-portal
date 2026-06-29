/**
 * IELTS Study Portal — Vocabulary Deck Builder & Adapter
 *
 * Groups the flat vocabulary list into study decks, then adapts them
 * into a consistent structure for the vocabulary page UI with
 * category classification, progress tracking, sorting, and filtering.
 */

const VOCAB_DECK_TARGET_SIZE = 24;

// ── Legacy theme category config (kept for buildVocabularyDecks) ──
const THEME_CATEGORY_CONFIG = {
  academic: {
    title: '学术研究核心词汇',
    tag: 'Academic',
    match: function (theme) {
      return /Academic|Education|Research|Knowledge|Science/i.test(theme);
    },
  },
  economy: {
    title: '经济商业高频词汇',
    tag: 'Business',
    match: function (theme) {
      return /Economy|Trade|Finance|Business/i.test(theme);
    },
  },
  society: {
    title: '社会治理与可持续发展词汇',
    tag: 'Society',
    match: function (theme) {
      return /Technology|Environment|Social|Politics|Governance|Law|Policy|Culture|Health|Medicine/i.test(theme);
    },
  },
};

// ── Category metadata for the vocabulary page UI ──────────────────
var CATEGORY_META = {
  'ielts-academic-core': { label: 'Academic Core', icon: '📚', color: 'blue',   order: 0 },
  'listening-scene':     { label: '听力场景',      icon: '🎧', color: 'green',  order: 1 },
  'reading-synonym':     { label: '阅读同义替换',  icon: '📖', color: 'purple', order: 2 },
  'reading-keyword':     { label: '阅读考点词',    icon: '📝', color: 'orange', order: 3 },
  'writing':             { label: '写作词汇',      icon: '✍️', color: 'indigo', order: 4 },
  'speaking':            { label: '口语词汇',      icon: '💬', color: 'pink',   order: 5 },
  'other':               { label: '其他词包',      icon: '📋', color: 'slate',  order: 99 },
};

// ── Category color → Tailwind class mapping ───────────────────────
var CATEGORY_COLORS = {
  blue:   { bg: 'bg-blue-50',  text: 'text-blue-700',  ring: 'ring-blue-200',  active: 'bg-blue-600 text-white' },
  green:  { bg: 'bg-green-50', text: 'text-green-700', ring: 'ring-green-200', active: 'bg-green-600 text-white' },
  purple: { bg: 'bg-purple-50',text: 'text-purple-700',ring: 'ring-purple-200',active: 'bg-purple-600 text-white' },
  orange: { bg: 'bg-orange-50',text: 'text-orange-700',ring: 'ring-orange-200',active: 'bg-orange-600 text-white' },
  indigo: { bg: 'bg-indigo-50',text: 'text-indigo-700',ring: 'ring-indigo-200',active: 'bg-indigo-600 text-white' },
  pink:   { bg: 'bg-pink-50', text: 'text-pink-700',  ring: 'ring-pink-200',  active: 'bg-pink-600 text-white' },
  slate:  { bg: 'bg-slate-50',text: 'text-slate-600', ring: 'ring-slate-200', active: 'bg-slate-600 text-white' },
};

// ── Helpers ───────────────────────────────────────────────────────
function slugifyDeckPart(value) {
  return String(value || 'general')
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'general';
}

function getWordCategory(word) {
  var source = word.source || word.book || word.origin;
  if (source) {
    return {
      key: 'source-' + slugifyDeckPart(source),
      title: source + ' 核心词汇',
      tag: source,
    };
  }

  var theme = word.theme || 'Core Academic';
  var configKeys = Object.keys(THEME_CATEGORY_CONFIG);
  for (var i = 0; i < configKeys.length; i++) {
    var config = THEME_CATEGORY_CONFIG[configKeys[i]];
    if (config.match(theme)) {
      return {
        key: configKeys[i],
        title: config.title,
        tag: config.tag,
      };
    }
  }

  return {
    key: 'general',
    title: 'IELTS 综合核心词汇',
    tag: 'Core',
  };
}

function chooseDeckCount(total) {
  if (total <= 30) return 1;
  var deckCount = Math.max(1, Math.ceil(total / VOCAB_DECK_TARGET_SIZE));
  while (deckCount > 1 && Math.floor(total / deckCount) < 20) {
    deckCount -= 1;
  }
  return deckCount;
}

function chunkWordsForDecks(words) {
  var deckCount = chooseDeckCount(words.length);
  var baseSize = Math.floor(words.length / deckCount);
  var remainder = words.length % deckCount;
  var chunks = [];
  var cursor = 0;

  for (var i = 0; i < deckCount; i++) {
    var size = baseSize + (i < remainder ? 1 : 0);
    chunks.push(words.slice(cursor, cursor + size));
    cursor += size;
  }

  return chunks;
}

// ── Legacy: buildVocabularyDecks (used by vocab-deck.html) ────────
function buildVocabularyDecks(words) {
  var grouped = new Map();

  words.forEach(function (word, index) {
    var category = getWordCategory(word);
    if (!grouped.has(category.key)) {
      grouped.set(category.key, {
        key: category.key,
        title: category.title,
        tag: category.tag,
        words: [],
        firstIndex: index,
      });
    }
    grouped.get(category.key).words.push(word);
  });

  var categories = Array.from(grouped.values()).sort(function (a, b) {
    return a.firstIndex - b.firstIndex;
  });

  var decks = [];
  categories.forEach(function (category) {
    var chunks = chunkWordsForDecks(category.words);
    chunks.forEach(function (chunk, chunkIndex) {
      var partNumber = chunkIndex + 1;
      var id = category.key + '-part-' + partNumber;
      decks.push({
        id: id,
        title: category.title + ' Part ' + partNumber,
        categoryTitle: category.title,
        tag: category.tag,
        part: partNumber,
        totalParts: chunks.length,
        wordCount: chunk.length,
        words: chunk,
      });
    });
  });

  return decks;
}

function findVocabularyDeck(decks, deckId) {
  return decks.find(function (deck) {
    return deck.id === deckId;
  }) || null;
}

// ═══════════════════════════════════════════════════════════════════
// ── NEW: Category classification ──────────────────────────────────
// ═══════════════════════════════════════════════════════════════════

/**
 * getDeckCategory(deck) → category key string
 *
 * Classifies a deck based on its source tag. Checks the first word's
 * `source` field (all words in a deck share the same source).
 */
function getDeckCategory(deck) {
  var source = '';
  if (deck.words && deck.words.length > 0 && deck.words[0].source) {
    source = deck.words[0].source;
  }
  // Fallback: inspect the deck tag
  if (!source && deck.tag) {
    source = deck.tag;
  }

  // Writing
  if (/写作/i.test(source)) return 'writing';
  // Speaking
  if (/口语/i.test(source)) return 'speaking';
  // Listening scenes (地图, 场景)
  if (/听力.*(?:场景|地图)/i.test(source) || /地图题/i.test(source)) return 'listening-scene';
  // Listening keyword (179, 考点)
  if (/听力/i.test(source)) return 'listening-scene';
  // Reading synonym (同义替换, 99组)
  if (/阅读/i.test(source) && /(?:同义|99组)/i.test(source)) return 'reading-synonym';
  // Reading keyword (考点, 538)
  if (/阅读/i.test(source) && /(?:考点|538)/i.test(source)) return 'reading-keyword';
  // Broader reading source
  if (/阅读/i.test(source)) return 'reading-keyword';
  // Academic Core (9400, 核心词汇库, Academic Core)
  if (/Academic Core/i.test(source) || /核心词汇库/i.test(source) || /9400/i.test(source)) return 'ielts-academic-core';
  // Any other Academic Core keyword
  if (/核心词/i.test(source) || /Core/i.test(source)) return 'ielts-academic-core';

  return 'other';
}

/**
 * getCategoryMeta(categoryKey) → { label, icon, color, order }
 */
function getCategoryMeta(categoryKey) {
  return CATEGORY_META[categoryKey] || CATEGORY_META['other'];
}

/**
 * getCategoryColorClasses(categoryKey) → { bg, text, ring, active }
 */
function getCategoryColorClasses(categoryKey) {
  var meta = getCategoryMeta(categoryKey);
  return CATEGORY_COLORS[meta.color] || CATEGORY_COLORS['slate'];
}

// ═══════════════════════════════════════════════════════════════════
// ── NEW: Deck adapter (raw deck → UI-ready deck) ──────────────────
// ═══════════════════════════════════════════════════════════════════

/**
 * adaptVocabularyDecks(rawDecks)
 *
 * Takes the output of buildVocabularyDecks() and enriches each deck
 * with UI metadata: category classification, preview words, sort order,
 * recommended flag, and status.
 */
function adaptVocabularyDecks(rawDecks) {
  if (!rawDecks || !rawDecks.length) return [];

  return rawDecks.map(function (deck) {
    var categoryKey = getDeckCategory(deck);
    var meta = getCategoryMeta(categoryKey);
    var previewWords = (deck.words || []).slice(0, 3);

    return {
      // Original fields (preserved for backward compat)
      id: deck.id,
      title: deck.title,
      categoryTitle: deck.categoryTitle,
      tag: deck.tag,
      part: deck.part,
      totalParts: deck.totalParts,
      wordCount: deck.wordCount,
      words: deck.words,

      // New UI fields
      category: categoryKey,
      categoryLabel: meta.label,
      categoryIcon: meta.icon,
      categoryColor: meta.color,
      previewWords: previewWords,
      recommended: categoryKey === 'ielts-academic-core' && deck.part === 1,
      sortOrder: meta.order * 10000 + (deck.part || 0),
    };
  });
}

/**
 * getRecommendedDeck(decks) — first Academic Core part-1 deck, or first deck.
 */
function getRecommendedDeck(decks) {
  if (!decks || !decks.length) return null;
  var recommended = decks.find(function (d) { return d.recommended; });
  return recommended || decks[0];
}

// ═══════════════════════════════════════════════════════════════════
// ── NEW: localStorage progress helpers ────────────────────────────
// ═══════════════════════════════════════════════════════════════════

var LS_LAST_DECK = 'vocab_last_deck';
var LS_PROGRESS_PREFIX = 'vocab_progress_';

function getLastStudiedDeckId() {
  try {
    return localStorage.getItem(LS_LAST_DECK) || null;
  } catch (e) {
    return null;
  }
}

function setLastStudiedDeckId(deckId) {
  try {
    localStorage.setItem(LS_LAST_DECK, deckId);
  } catch (e) { /* ignore */ }
}

function getLastStudiedDeck(decks) {
  var lastId = getLastStudiedDeckId();
  if (!lastId) return null;
  return decks.find(function (d) { return d.id === lastId; }) || null;
}

function getDeckProgress(deckId) {
  try {
    var raw = localStorage.getItem(LS_PROGRESS_PREFIX + deckId);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

function getDeckStatus(deckId) {
  var progress = getDeckProgress(deckId);
  if (!progress) return 'not-started';
  var statuses = progress.status || {};
  var keys = Object.keys(statuses);
  if (keys.length === 0) return 'not-started';
  var hasUnseen = false;
  var hasKnown = false;
  var hasUnknown = false;
  for (var k in statuses) {
    if (statuses[k] === 'unseen') hasUnseen = true;
    if (statuses[k] === 'known') hasKnown = true;
    if (statuses[k] === 'unknown') hasUnknown = true;
  }
  // If all words have been judged (no unseen), consider it complete
  if (!hasUnseen && keys.length > 0) return 'completed';
  // If any words have been judged, in progress
  if (hasKnown || hasUnknown) return 'in-progress';
  return 'not-started';
}

function getStudyStats(decks) {
  var totalJudged = 0;
  var totalUnknown = 0;
  decks.forEach(function (deck) {
    var progress = getDeckProgress(deck.id);
    if (!progress || !progress.status) return;
    var statuses = progress.status;
    for (var k in statuses) {
      if (statuses[k] === 'known') totalJudged++;
      if (statuses[k] === 'unknown') { totalJudged++; totalUnknown++; }
    }
  });
  return { studiedCount: totalJudged, reviewCount: totalUnknown };
}

// ═══════════════════════════════════════════════════════════════════
// ── NEW: Sort & filter helpers ────────────────────────────────────
// ═══════════════════════════════════════════════════════════════════

function sortDecks(decks, sortBy) {
  var sorted = decks.slice();
  switch (sortBy) {
    case 'wordCount-asc':
      sorted.sort(function (a, b) { return a.wordCount - b.wordCount; });
      break;
    case 'wordCount-desc':
      sorted.sort(function (a, b) { return b.wordCount - a.wordCount; });
      break;
    case 'alpha':
      sorted.sort(function (a, b) {
        return (a.title || '').localeCompare(b.title || '', 'zh-CN');
      });
      break;
    case 'recommended':
    default:
      sorted.sort(function (a, b) {
        if (a.recommended && !b.recommended) return -1;
        if (!a.recommended && b.recommended) return 1;
        return (a.sortOrder || 0) - (b.sortOrder || 0);
      });
      break;
  }
  return sorted;
}

function filterDecksByCategory(decks, category) {
  if (!category || category === 'all') return decks;
  return decks.filter(function (d) { return d.category === category; });
}

function filterDecksBySearch(decks, query) {
  if (!query || !query.trim()) return decks;
  var q = query.trim().toLowerCase();
  return decks.filter(function (deck) {
    // Match deck title
    if ((deck.title || '').toLowerCase().indexOf(q) !== -1) return true;
    // Match category title
    if ((deck.categoryTitle || '').toLowerCase().indexOf(q) !== -1) return true;
    // Match tag
    if ((deck.tag || '').toLowerCase().indexOf(q) !== -1) return true;
    // Match preview words
    return (deck.previewWords || []).some(function (w) {
      return (w.word || '').toLowerCase().indexOf(q) !== -1 ||
             (w.chinese || '').indexOf(q) !== -1;
    });
  });
}

function filterDecksByStatus(decks, status) {
  if (!status || status === 'all') return decks;
  return decks.filter(function (d) {
    return getDeckStatus(d.id) === status;
  });
}

// ═══════════════════════════════════════════════════════════════════
// ── Exports ───────────────────────────────────────────────────────
// ═══════════════════════════════════════════════════════════════════

// Legacy (used by vocab-deck.html)
window.buildVocabularyDecks = buildVocabularyDecks;
window.findVocabularyDeck = findVocabularyDeck;

// New (used by vocabulary.html)
window.getDeckCategory = getDeckCategory;
window.CATEGORY_META = CATEGORY_META;
window.getCategoryMeta = getCategoryMeta;
window.getCategoryColorClasses = getCategoryColorClasses;
window.adaptVocabularyDecks = adaptVocabularyDecks;
window.getRecommendedDeck = getRecommendedDeck;

// Progress
window.getLastStudiedDeckId = getLastStudiedDeckId;
window.setLastStudiedDeckId = setLastStudiedDeckId;
window.getLastStudiedDeck = getLastStudiedDeck;
window.getDeckProgress = getDeckProgress;
window.getDeckStatus = getDeckStatus;
window.getStudyStats = getStudyStats;

// Sort & filter
window.sortDecks = sortDecks;
window.filterDecksByCategory = filterDecksByCategory;
window.filterDecksBySearch = filterDecksBySearch;
window.filterDecksByStatus = filterDecksByStatus;
