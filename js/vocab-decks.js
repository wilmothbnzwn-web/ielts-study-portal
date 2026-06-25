/**
 * IELTS Study Portal — Vocabulary Deck Builder
 *
 * Groups the flat vocabulary list into study decks. Words with explicit
 * `source` metadata stay source-based; the current static vocabulary falls
 * back to broad IELTS themes and is chunked into 20-30 word decks.
 */

const VOCAB_DECK_TARGET_SIZE = 24;

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

function slugifyDeckPart(value) {
  return String(value || 'general')
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'general';
}

function getWordCategory(word) {
  const source = word.source || word.book || word.origin;
  if (source) {
    return {
      key: 'source-' + slugifyDeckPart(source),
      title: source + ' 核心词汇',
      tag: source,
    };
  }

  const theme = word.theme || 'Core Academic';
  const configKeys = Object.keys(THEME_CATEGORY_CONFIG);
  for (var i = 0; i < configKeys.length; i++) {
    const config = THEME_CATEGORY_CONFIG[configKeys[i]];
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
  let deckCount = Math.max(1, Math.ceil(total / VOCAB_DECK_TARGET_SIZE));
  while (deckCount > 1 && Math.floor(total / deckCount) < 20) {
    deckCount -= 1;
  }
  return deckCount;
}

function chunkWordsForDecks(words) {
  const deckCount = chooseDeckCount(words.length);
  const baseSize = Math.floor(words.length / deckCount);
  const remainder = words.length % deckCount;
  const chunks = [];
  let cursor = 0;

  for (var i = 0; i < deckCount; i++) {
    const size = baseSize + (i < remainder ? 1 : 0);
    chunks.push(words.slice(cursor, cursor + size));
    cursor += size;
  }

  return chunks;
}

function buildVocabularyDecks(words) {
  const grouped = new Map();

  words.forEach(function (word, index) {
    const category = getWordCategory(word);
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

  const categories = Array.from(grouped.values()).sort(function (a, b) {
    return a.firstIndex - b.firstIndex;
  });

  const decks = [];
  categories.forEach(function (category) {
    const chunks = chunkWordsForDecks(category.words);
    chunks.forEach(function (chunk, chunkIndex) {
      const partNumber = chunkIndex + 1;
      const id = category.key + '-part-' + partNumber;
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

window.buildVocabularyDecks = buildVocabularyDecks;
window.findVocabularyDeck = findVocabularyDeck;
