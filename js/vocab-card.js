/**
 * IELTS Study Portal — Shared VocabCard Component
 *
 * Reusable vocabulary card with 3D flip animation, audio playback,
 * and theme-aware styling. Used by both vocabulary.html and collection.html.
 *
 * Usage:
 *   const html = VocabCard(wordData, options);
 *   // => HTML string ready for innerHTML injection
 */

// ── Theme Color Map ────────────────────────────────────────────
const THEME_COLORS = {
  'Academic & Research':    'bg-purple-50 text-purple-700',
  'Economy & Trade':        'bg-blue-50 text-blue-700',
  'Environment & Development': 'bg-green-50 text-green-700',
  'Social Development':     'bg-orange-50 text-orange-700',
  'Technology & Society':   'bg-cyan-50 text-cyan-700',
  'Politics & Governance':  'bg-red-50 text-red-700',
  'Economy & Policy':       'bg-blue-50 text-blue-700',
  'Economy & Finance':      'bg-blue-50 text-blue-700',
  'Environment & Energy':   'bg-green-50 text-green-700',
  'Environment & Policy':   'bg-green-50 text-green-700',
  'Education & Knowledge':  'bg-indigo-50 text-indigo-700',
  'Health & Medicine':      'bg-rose-50 text-rose-700',
  'Law & Policy':           'bg-red-50 text-red-700',
  'Culture & Society':      'bg-orange-50 text-orange-700',
  'Technology & Change':    'bg-cyan-50 text-cyan-700',
  'Technology & Work':      'bg-cyan-50 text-cyan-700',
  'Politics & Trade':       'bg-red-50 text-red-700',
  'Politics & Society':     'bg-red-50 text-red-700',
  'Economy & Business':     'bg-blue-50 text-blue-700',
  'Economy & Development':  'bg-blue-50 text-blue-700',
  'Education & Science':    'bg-indigo-50 text-indigo-700',
};

function getThemeColor(theme) {
  return THEME_COLORS[theme] || 'bg-brand-50 text-brand-700';
}

// ── Helpers ────────────────────────────────────────────────────

function escapeHtml(str) {
  if (str == null) return '';
  const div = document.createElement('div');
  div.textContent = String(str);
  return div.innerHTML;
}

function escapeJsString(str) {
  return String(str == null ? '' : str)
    .replace(/\\/g, '\\\\')
    .replace(/'/g, "\\'")
    .replace(/\n/g, '\\n')
    .replace(/\r/g, '\\r');
}

function renderDifficultyDots(level) {
  if (!level || level < 1) return '';
  return Array.from({ length: 5 }, function (_, i) {
    var cls = i < level ? 'difficulty-dot filled' : 'difficulty-dot empty';
    return '<span class="' + cls + '"></span>';
  }).join('');
}

/**
 * VocabCard — Generate a vocabulary card HTML string.
 *
 * @param {Object}  w                      — Word data
 * @param {string}  w.word                 — The word
 * @param {string}  w.chinese              — Chinese translation
 * @param {string}  [w.pos]                — Part of speech
 * @param {string}  [w.phonetic]           — IPA phonetic
 * @param {string}  [w.audioUrl]           — Pronunciation audio URL
 * @param {string[]} [w.synonyms]          — Synonym list
 * @param {string}  [w.definition]         — English definition (front)
 * @param {string}  [w.example]            — Example sentence (back)
 * @param {string}  [w.contextSentence]    — Fallback for definition & example
 * @param {string}  [w.contextHtml]        — Raw HTML override for front context display
 * @param {string}  [w.theme]              — Theme/category
 * @param {number}  [w.difficulty]         — Difficulty 1–5
 *
 * @param {Object}  [opts]                 — Options
 * @param {boolean} [opts.flippable=true]  — Enable 3D flip
 * @param {boolean} [opts.showAudio=true]  — Show audio button
 * @param {boolean} [opts.showDelete=false]— Show delete button
 * @param {boolean} [opts.showTimestamp=false] — Show saved-at timestamp
 * @param {string}  [opts.cardIdPrefix='vocab'] — DOM id prefix
 * @param {number}  [opts.savedAt]         — Timestamp for display
 *
 * @returns {string} HTML
 */
function VocabCard(w, opts) {
  opts = opts || {};
  var flippable     = opts.flippable !== false;
  var showAudio     = opts.showAudio !== false;
  var showDelete    = opts.showDelete === true;
  var showTimestamp = opts.showTimestamp === true;
  var cardIdPrefix  = opts.cardIdPrefix || 'vocab';
  var savedAt       = opts.savedAt || null;

  var cardId = cardIdPrefix + '-' + (w.id != null ? w.id : w.word);
  var tc = getThemeColor(w.theme);
  var hasFlipContent = (w.synonyms && w.synonyms.length > 0) || w.example || w.contextSentence;

  // ── Front-side elements ──

  // Part of speech
  var posHtml = w.pos
    ? '<p class="text-xs text-brand-400 italic">' + escapeHtml(w.pos) + '</p>'
    : '';

  // Theme badge
  var themeHtml = w.theme
    ? '<span class="theme-badge ' + tc + ' flex-shrink-0">' + escapeHtml(w.theme) + '</span>'
    : '';

  // Phonetic
  var phoneticHtml = w.phonetic
    ? '<span class="text-xs text-brand-400 font-mono ml-1">' + escapeHtml(w.phonetic) + '</span>'
    : '';

  // Audio button
  var audioHtml = '';
  if (showAudio && (w.audioUrl || w.word)) {
    if (w.audioUrl) {
      audioHtml = '<button class="audio-btn flex-shrink-0" id="audio-' + cardId + '" onclick="event.stopPropagation(); playAudio(\'' + escapeJsString(cardId) + '\',\'' + escapeJsString(w.audioUrl) + '\')" title="播放发音">🔊</button>';
    } else {
      audioHtml = '<button class="audio-btn flex-shrink-0" id="audio-' + cardId + '" onclick="event.stopPropagation(); speakWord(\'' + escapeJsString(cardId) + '\',\'' + escapeJsString(w.word) + '\')" title="播放发音">🔊</button>';
    }
  }

  // Definition / context sentence on front
  var frontText = '';
  var frontIsHtml = false;
  if (w.definition) {
    frontText = escapeHtml(w.definition);
  } else if (w.contextHtml) {
    frontText = w.contextHtml;
    frontIsHtml = true;
  } else if (w.contextSentence) {
    frontText = escapeHtml(w.contextSentence);
  }
  var definitionHtml = frontText
    ? '<div class="text-xs text-brand-400 leading-relaxed line-clamp-3 break-words">' + frontText + '</div>'
    : '';

  // Difficulty dots
  var dotsHtml = w.difficulty
    ? '<div class="mt-3 flex items-center gap-1" title="Difficulty: ' + w.difficulty + '/5">' + renderDifficultyDots(w.difficulty) + '</div>'
    : '';

  // Flip hint
  var flipHintHtml = (flippable && hasFlipContent)
    ? '<p class="text-xs text-brand-300 mt-3">点击翻转查看同义词 & 例句 →</p>'
    : '';

  // Timestamp
  var timestampHtml = '';
  if (showTimestamp && savedAt) {
    timestampHtml = '<p class="text-xs text-brand-300 mt-2">' + new Date(savedAt).toLocaleString('zh-CN') + '</p>';
  }

  // Delete button
  var deleteHtml = '';
  if (showDelete) {
    deleteHtml = '<button class="text-xs text-brand-300 hover:text-red-500 transition-colors flex-shrink-0 mt-1" onclick="event.stopPropagation(); deleteWord(' + w.id + ')" title="删除">🗑</button>';
  }

  // ── Build front side ──
  var frontHtml =
    '<div class="flex items-start justify-between mb-2 sm:mb-3 gap-2">' +
      '<div class="min-w-0 flex-1">' +
        '<div class="flex items-center gap-2 flex-wrap">' +
          '<h3 class="text-base sm:text-lg font-bold text-brand-900 font-serif truncate">' + escapeHtml(w.word) + '</h3>' +
          phoneticHtml +
          audioHtml +
        '</div>' +
        posHtml +
      '</div>' +
      '<div class="flex items-start gap-2 flex-shrink-0">' +
        themeHtml +
        deleteHtml +
      '</div>' +
    '</div>' +
    '<p class="text-sm text-brand-600 font-medium mb-2">' + escapeHtml(w.chinese || '') + '</p>' +
    definitionHtml +
    dotsHtml +
    flipHintHtml +
    timestampHtml;

  // ── Non-flippable or no back content → flat card ──
  if (!flippable || !hasFlipContent) {
    return '<div class="vocab-card bg-white rounded-2xl border border-brand-100 p-4 sm:p-5 max-w-full overflow-hidden min-h-[16rem]" id="' + cardId + '">' + frontHtml + '</div>';
  }

  // ── Back side ──
  var synonymsHtml = '';
  if (w.synonyms && w.synonyms.length > 0) {
    var tags = '';
    for (var i = 0; i < w.synonyms.length; i++) {
      tags += '<span class="text-xs bg-white text-brand-700 px-2 py-1 rounded-md border border-brand-100">' + escapeHtml(w.synonyms[i]) + '</span>';
    }
    synonymsHtml = '<div class="flex flex-wrap gap-1 sm:gap-1.5 mb-3 sm:mb-4">' + tags + '</div>';
  }

  var exampleText = w.example || w.contextSentence || '';
  var exampleHtml = exampleText
    ? '<p class="text-sm text-brand-700 leading-relaxed italic break-words">"' + escapeHtml(exampleText) + '"</p>'
    : '';

  var backHtml =
    '<div class="card-back bg-brand-50 rounded-2xl p-4 sm:p-5 flex flex-col overflow-y-auto">' +
      '<p class="text-xs font-semibold text-brand-400 uppercase tracking-wide mb-2">Synonyms</p>' +
      synonymsHtml +
      '<p class="text-xs font-semibold text-brand-400 uppercase tracking-wide mb-1">Example</p>' +
      exampleHtml +
      '<p class="text-xs text-brand-300 mt-auto pt-3">点击翻转回到正面 →</p>' +
    '</div>';

  // Check flip state
  var isFlipped = window._vocabCardFlipped && window._vocabCardFlipped.has(cardId);

  return '<div class="card vocab-card bg-white rounded-2xl border border-brand-100 p-4 sm:p-5 max-w-full overflow-hidden min-h-[16rem]" id="' + cardId + '" onclick="toggleCard(\'' + cardId + '\')">' +
    '<div class="card-inner" style="transform:' + (isFlipped ? 'rotateY(180deg)' : 'none') + '">' +
      '<div class="card-front overflow-hidden">' + frontHtml + '</div>' +
      backHtml +
    '</div>' +
  '</div>';
}

// ── Global flip state & toggle ─────────────────────────────────
if (!window._vocabCardFlipped) {
  window._vocabCardFlipped = new Set();
}

function toggleCard(cardId) {
  var flipped = window._vocabCardFlipped;
  if (flipped.has(cardId)) {
    flipped.delete(cardId);
  } else {
    flipped.add(cardId);
  }
  var card = document.getElementById(cardId);
  if (card) {
    var inner = card.querySelector('.card-inner');
    if (inner) {
      inner.style.transform = flipped.has(cardId) ? 'rotateY(180deg)' : 'none';
    }
  }
}

// ── Shared audio playback ──────────────────────────────────────
var _currentAudio = null;

function playAudio(cardId, url) {
  if (!url) return;
  if (_currentAudio) {
    _currentAudio.pause();
    _currentAudio = null;
  }
  // Reset all audio buttons
  var allBtns = document.querySelectorAll('.audio-btn');
  for (var i = 0; i < allBtns.length; i++) {
    allBtns[i].classList.remove('playing');
  }

  var audio = new Audio(url);
  _currentAudio = audio;
  var btn = document.getElementById('audio-' + cardId);
  if (btn) btn.classList.add('playing');

  audio.play().catch(function () {
    if (btn) btn.classList.remove('playing');
  });
  audio.onended = function () {
    if (btn) btn.classList.remove('playing');
    _currentAudio = null;
  };
  audio.onerror = function () {
    if (btn) btn.classList.remove('playing');
    _currentAudio = null;
  };
}

function speakWord(cardId, word) {
  if (!word || !window.speechSynthesis) return;
  if (_currentAudio) {
    _currentAudio.pause();
    _currentAudio = null;
  }
  window.speechSynthesis.cancel();

  var allBtns = document.querySelectorAll('.audio-btn');
  for (var i = 0; i < allBtns.length; i++) {
    allBtns[i].classList.remove('playing');
  }

  var btn = document.getElementById('audio-' + cardId);
  if (btn) btn.classList.add('playing');

  var utterance = new SpeechSynthesisUtterance(word);
  utterance.lang = 'en-US';
  utterance.rate = 0.88;
  utterance.onend = function () {
    if (btn) btn.classList.remove('playing');
  };
  utterance.onerror = function () {
    if (btn) btn.classList.remove('playing');
  };
  window.speechSynthesis.speak(utterance);
}

window.VocabCard = VocabCard;
window.toggleCard = toggleCard;
window.playAudio = playAudio;
window.speakWord = speakWord;
