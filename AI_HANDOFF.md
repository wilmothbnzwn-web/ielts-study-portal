# AI Handoff Document — IELTS Study Portal

> **Read this first** if you are a new AI Agent taking over this project.
> Every technical decision, API route, data structure, and known limitation is documented below.

---

## 1. Project Overview

| Field | Value |
|-------|-------|
| **Project Name** | IELTS Study Portal |
| **Purpose** | IELTS Academic (A类) Reading & Writing self-study platform for Chinese-speaking learners |
| **Production URL** | `https://elaborate-duckanoo-d25740.netlify.app` |
| **GitHub Repo** | `https://github.com/wilmothbnzwn-web/ielts-study-portal` (Private) |
| **Deploy Platform** | Netlify (auto-deploy on `git push` to `main`) |
| **Local Dev Port** | `3456` (start with `node server.js` or `npm start`) |
| **Last Updated** | 2026-06-15 |
| **Total Commits** | 6 (see §12 Git History) |

---

## 2. Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| **Frontend** | Pure HTML/CSS/JS (no framework) | 6 standalone `.html` pages + 1 shared JS component |
| **Shared Components** | `js/vocab-card.js` — VocabCard() | Reusable 3D-flip vocabulary card used by both vocabulary.html & collection.html |
| **CSS** | Tailwind CSS via CDN (`cdn.tailwindcss.com`) | Custom `brand` color palette + `serif`/`sans` font families configured inline |
| **Backend (local)** | Node.js `http` module — zero npm dependencies | `server.js` serves static files + 2 dynamic proxy routes + 7 static JSON API routes |
| **Backend (production)** | Netlify Serverless Functions | 9 functions under `netlify/functions/`, auto-deployed |
| **Data Layer** | Static JSON files in `data/` | 7 files; no database |
| **Persistence (client)** | `localStorage` | Two keys: `ielts_myWords` and `ielts_mySentences` |
| **External APIs (proxied)** | MyMemory Translation API, Free Dictionary API | Both called server-side to avoid CORS |
| **package.json** | `{ "scripts": { "start": "node server.js", "dev": "node server.js" } }` | Zero `dependencies` / `devDependencies` |

---

## 3. Project File Tree

```
IELTS_Study_Portal/
├── index.html                          # Landing page (hero + 3 feature cards)
├── mock-test.html                      # ★ NEW: Computer-delivered IELTS reading mock test (split-pane, timer, highlighting, bottom nav)
├── writing.html                        # Writing methodology (3 tabs: descriptors, Simon, essays)
├── reading.html                        # Reading training (5 articles + translation + collection)
├── vocabulary.html                     # 288 IELTS vocabulary cards (filterable, flip animation, VocabCard component)
├── collection.html                     # My Collection (word tabs use VocabCard + sentence tabs, localStorage)
├── server.js                           # Local dev server (port 3456, all API routes)
├── js/
│   └── vocab-card.js                   # Shared VocabCard component + playAudio() + toggleCard()
├── package.json                        # Minimal, zero deps
├── netlify.toml                        # Netlify config: build, functions, redirects
├── vercel.json                         # Vercel fallback (UNUSED — left from early attempt)
├── .gitignore                          # node_modules, .env, .vercel, .netlify, .DS_Store
│
├── data/                               # Static JSON data files (7 files)
│   ├── dictionary.json                 # 558-entry EN→ZH word dictionary
│   ├── vocabulary.json                 # 50 IELTS core words with full metadata
│   ├── reading-articles.json           # 5 academic articles with vocab highlights
│   ├── essays.json                     # 3 Band 8+ sample essays
│   ├── methodology.json                # Simon's writing methodology content
│   ├── band-descriptors.json           # Official IELTS band descriptors
│   └── mock-test-1.json                # ★ NEW: Cam 9 Test 1 mock exam (passage + 13 questions)
│
├── api/                                # LEGACY Vercel serverless functions (UNUSED)
│   ├── band-descriptors.js
│   ├── essays.js
│   ├── methodology.js
│   ├── reading-articles.js
│   └── vocabulary.js
│
└── netlify/functions/                  # Active Netlify serverless functions (9 files)
    ├── band-descriptors.js             # Serves data/band-descriptors.json
    ├── essays.js                       # Serves data/essays.json
    ├── methodology.js                  # Serves data/methodology.json
    ├── reading-articles.js             # Serves data/reading-articles.json
    ├── vocabulary.js                   # Serves data/vocabulary.json
    ├── dictionary.js                   # Serves data/dictionary.json
    ├── mock-test-1.js                  # ★ NEW: Serves data/mock-test-1.json
    ├── translate.js                    # Proxies MyMemory Translation API
    └── dictionary-lookup.js            # Proxies Free Dictionary API
```

---

## 4. New Module: Computer-Delivered Mock Test (机考模拟)

### 4.1 Overview

`mock-test.html` is a standalone simulation of the official IELTS computer-delivered Reading test interface, built from web research on the 2025 updated IDP/British Council system. It uses the same zero-dependency architecture (pure HTML/CSS/JS + Tailwind CDN).

### 4.2 UI Layout (Research-Backed)

Based on research of the official IDP/British Council computer-based IELTS interface (2024-2025 updates):

| UI Element | Implementation |
|------------|---------------|
| **Top bar** | Dark (#1a1a2e) exam bar with Test label, Section indicator, centered countdown timer, Aa/Help/Submit buttons |
| **Split pane** | 50:50 left-right flex layout. Left = passage (independent scroll), Right = questions (independent scroll). Resizable divider planned for v2. |
| **Bottom navigator** | Fixed 56px bar with 1-40 question number blocks. Answered = green underline, Current = dark filled, Passage 2/3 placeholders shown at 40% opacity. Arrow buttons + Tab/Arrow key keyboard nav. |
| **Timer** | Monospace font, 60:00 → counts down. Yellow pulse warning at 10 min remaining, red pulse danger at 5 min. Auto-submits at 0:00. |
| **Font size** | 3-level toggle (16px/18px/20px) — matching official accessibility feature. |

### 4.3 Core Interaction: Text Highlighting

```
User selects text in passage pane (mouseup)
        │
        ▼
  'mouseup' event fires → 10ms setTimeout
        │
        ▼
  Validate: selection is non-empty AND inside #passage-pane
        │
        ▼
  Tooltip appears near selection rect → "🖊 高亮" + "✕ 清除" buttons
        │
        ▼
  Click "高亮" → Range.surroundContents(<span class="highlighted">)
  (fallback: extractContents + insertNode for cross-element selections)
        │
        ▼
  Click "清除" → unwrap highlighted span, restore text nodes
        │
        ▼
  Tooltip hides on: click outside, scroll, or Escape
```

**Known limitation for MVP**: Highlights are DOM-only (not persisted across passage re-renders). In production, could serialize highlight positions as character offsets and reapply on re-render.

### 4.4 Question Types Implemented (MVP)

| Type | UI Component | Validation |
|------|-------------|------------|
| **TRUE/FALSE/NOT GIVEN** | 3-option button group (flex-wrap, equal width). Selected = filled border. After submit: green = correct, red = incorrect. | Exact index match (0=TRUE, 1=FALSE, 2=NOT GIVEN) |
| **Short Answer** | Text input (max 360px) with word limit hint in placeholder. After submit: green/red border + correct answer hint. | Case-insensitive trimmed string comparison |

### 4.5 Answer Tracking & Navigation

- **State**: `userAnswers = { questionId: answerValue }` — in-memory object, no localStorage persistence (matches exam behavior — answers lost on page leave).
- **Bottom nav**: Re-rendered on each answer change. `answered-nav` class applied when `userAnswers[qid]` is truthy.
- **Jump**: Click nav number → `scrollIntoView({ behavior: 'smooth', block: 'center' })` on corresponding question block.
- **Keyboard**: `Tab` = next question, `Ctrl+←` = prev, `Ctrl+→` = next.
- **Auto-save**: Every interaction (TFN click, text input) instantly saves to `userAnswers`.

### 4.6 Scoring & Review

```
User clicks ✓ (submit) or timer reaches 0:00
        │
        ▼
  Calculate: correct answers / total (13 MVP)
        │
        ▼
  Modal overlay: score fraction + percentage + encouragement message
        │
        ▼
  "查看答案" button: closes modal, shows green/red on each question
  "重新开始" button: resets all state (timer, answers, highlights)
```

### 4.7 Test Data Structure (`data/mock-test-1.json`)

Based on **Cambridge IELTS 9 Test 1 Passage 1** (William Henry Perkin — synthetic dyes). 13 questions covering 2 types:

```json
{
  "testId": "cam9-test1",
  "testName": "Cambridge IELTS 9 — Test 1",
  "totalTime": 3600,
  "passages": [{
    "id": 1,
    "title": "William Henry Perkin — The man who invented synthetic dyes",
    "passageText": "<p>...</p><p>...</p>",   // HTML-formatted, ~740 words
    "wordCount": 740,
    "questions": [
      { "id": 1, "type": "true_false_not_given", "questionText": "...", "options": ["TRUE","FALSE","NOT GIVEN"], "correctAnswer": 1 },
      { "id": 8, "type": "short_answer", "questionText": "...", "correctAnswer": "mauve", "wordLimit": 2 }
    ]
  }]
}
```

**Questions 1-7**: TRUE/FALSE/NOT GIVEN (TFN type) — 3-option radio-style buttons  
**Questions 8-13**: Short Answer — text inputs with word limit  
**Questions 14-40**: Placeholder (Passages 2 & 3 shown as "upcoming" at 40% opacity in navigator)

### 4.8 CSS Architecture

All styles are inline in `<style>` block (following project convention — no external CSS files). Key design tokens:

- `--panel-gutter: 0px` (reserved for future draggable divider)
- `.highlighted` — `background-color: #fef08a` (Tailwind yellow-200), hover darkens to `#fde047`
- `.nav-q-block` — 36×36px rounded blocks, gray border, answered = green 3px bottom border + green tinted bg
- `@keyframes timerPulse` — opacity oscillation for 10min/5min warnings
- Top bar: `#1a1a2e` (dark navy, matches official dark theme)
- Responsive: at 768px breakpoint, split pane becomes vertical stack (45%/55%)

### 4.9 Future Enhancements (v2)

| Feature | Notes |
|---------|-------|
| Draggable divider | Resize split ratio; `--panel-gutter` variable already declared |
| All 3 passages | Questions 14-40 with real passage content |
| More question types | Multiple choice, matching headings, sentence completion, Y/N/NG |
| Highlight persistence | Serialize as character offsets; survive re-renders |
| Audio for Listening | Full Listening test simulation with audio player |
| Writing test mode | Top-bottom split with word counter |
| Full test mode | Reading → Writing → Listening sequential flow |

---

## 5. API Architecture

### 9.1 Local Development (server.js)

`server.js` is a **zero-dependency** Node HTTP server. It handles requests in this order:

1. **Dynamic proxy routes** (intercept before static JSON mapping):
   - `GET /api/translate?text=<text>` — Proxies to `https://api.mymemory.translated.net/get?q=<cleaned>&langpair=en|zh`. Cleans text (strips `\n`, collapses whitespace) before forwarding. Returns `{ translatedText, match, source }`.
   - `GET /api/dictionary-lookup?word=<word>` — Proxies to `https://api.dictionaryapi.dev/api/v2/entries/en/<word>`. Returns `{ found, word, phonetic, audioUrl, synonyms[] }` or `{ found: false }` on 404/error.

2. **Static JSON API routes** (mapped from `API_ROUTES` object):
   - `GET /api/band-descriptors` → `data/band-descriptors.json`
   - `GET /api/vocabulary` → `data/vocabulary.json`
   - `GET /api/reading-articles` → `data/reading-articles.json`
   - `GET /api/essays` → `data/essays.json`
   - `GET /api/methodology` → `data/methodology.json`
   - `GET /api/mock-test-1` → `data/mock-test-1.json`
   - `GET /api/dictionary` → `data/dictionary.json`

3. **Static file serving**: Serves `.html` files from root directory. Falls back to `public/` (legacy), then to `index.html`.

### 9.2 Production (Netlify)

`netlify.toml` configuration:
```toml
[build]
  publish = "."

[functions]
  directory = "netlify/functions"
  included_files = ["data/**"]

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

- All `/api/*` requests are redirected to corresponding Netlify functions
- `included_files = ["data/**"]` ensures JSON data files are bundled with each function
- All functions use `process.cwd()` (NOT `__dirname`) for path resolution in the Lambda environment
- All functions return CORS headers (`Access-Control-Allow-Origin: *`)

### 9.3 Dual Deployment Pattern

Each API route exists in **two places** that must be kept in sync:
- `server.js` (local dev)
- `netlify/functions/<name>.js` (production)

When adding a new API route, you must update both.

---

## 7. Core Feature: Word Selection Translation (划词翻译)

### 9.1 Implementation Location
All translation logic lives in `reading.html` inline `<script>` (lines ~233–440).

### 9.2 Flow (end-to-end)

```
User selects text in article
        │
        ▼
  'mouseup' event fires
        │
        ▼
  Debounce check: clear previous timer, set new 400ms timer
  (variable: translateDebounceTimer)
        │
        ▼
  400ms passes with no new selection
        │
        ▼
  cleanText(): regex removes \n, \r, collapses \s+ → single spaces
        │
        ▼
  showLoadingTooltip(): renders tooltip with shimmer skeleton + spinner + "翻译中..."
        │
        ▼
  If single word → translateWord() checks local dictionary (558 entries)
        │
        ▼
  If not found → translateViaAPI() calls GET /api/translate?text=<cleaned>
  (backend proxies to MyMemory API, avoids CORS preflight)
        │
        ▼
  updateTooltip(): replaces skeleton with result + "📌 加入收藏" save button
        │
        ▼
  addToHistory(): adds to right-panel lookup history (max 20, deduped)
```

### 9.3 Key Functions

| Function | Purpose |
|----------|---------|
| `cleanText(text)` | Regex: `.replace(/[\n\r]+/g, ' ').replace(/\s+/g, ' ').trim()` |
| `showLoadingTooltip(rect, word)` | Creates fixed-position tooltip with skeleton shimmer animation |
| `updateTooltip(tooltip, word, translation)` | Replaces tooltip content with result + save button |
| `positionTooltip(tooltip, rect)` | Positions tooltip relative to selection, keeps within viewport |
| `translateWord(word)` | Case-insensitive lookup in `dictionary` object (single words only) |
| `translateViaAPI(text)` | Fetches `GET /api/translate?text=...` (backend proxy) |
| `escapeHtml(str)` | XSS-safe HTML escaping via `div.textContent` |

### 9.4 Tooltip Lifecycle

- **Open**: On debounced `mouseup` with valid selection in `#article-body`
- **Close**: Click outside tooltip, click ✕ button, scroll, or window resize
- **CSS**: `.tl-tooltip` — fixed position, z-index 9999, fadeIn animation, arrow pseudo-element

---

## 8. Shared Component: VocabCard (`js/vocab-card.js`)

### 9.1 Overview

`VocabCard(word, options)` is the shared vocabulary card renderer used by both `vocabulary.html` and `collection.html`. It generates a CSS 3D flip card with front (word info) and back (synonyms + example) sides.

### 9.2 Exports (global scope)

| Function | Purpose |
|----------|---------|
| `VocabCard(w, opts)` | Returns HTML string for a vocabulary card |
| `toggleCard(cardId)` | Flips card by setting inline `rotateY` transform on `.card-inner` |
| `playAudio(cardId, url)` | Plays pronunciation audio via HTML5 `Audio`, manages button pulse state |
| `getThemeColor(theme)` | Returns Tailwind CSS classes for theme badge |
| `renderDifficultyDots(level)` | Returns 1–5 difficulty dot HTML |

### 9.3 VocabCard Parameters

**Word data (`w`):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `word` | string | ✅ | The vocabulary word |
| `chinese` | string | ✅ | Chinese translation |
| `pos` | string | — | Part of speech (noun, verb, adjective…) |
| `phonetic` | string | — | IPA phonetic transcription |
| `audioUrl` | string | — | URL to pronunciation audio (triggers 🔊 button) |
| `synonyms` | string[] | — | Synonym list (displayed on back) |
| `definition` | string | — | English definition (front, line-clamp-2) |
| `example` | string | — | Example sentence (back) |
| `contextSentence` | string | — | Fallback for definition (front) AND example (back) |
| `contextHtml` | string | — | Raw HTML override for front context display (used for word highlighting in collection) |
| `theme` | string | — | Theme/category (renders as colored badge) |
| `difficulty` | number | — | Difficulty 1–5 (renders as dots) |

**Options (`opts`):**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `flippable` | boolean | `true` | Enables 3D flip to reveal synonyms/example on back |
| `showAudio` | boolean | `true` | Shows 🔊 audio button when `audioUrl` is present |
| `showDelete` | boolean | `false` | Shows 🗑 delete button (calls global `deleteWord(id)`) |
| `showTimestamp` | boolean | `false` | Shows saved-at timestamp below card content |
| `cardIdPrefix` | string | `'vocab'` | Prefix for DOM id (`${prefix}-${id}`) |
| `savedAt` | number | `null` | Timestamp for display when `showTimestamp` is true |

### 9.4 Card DOM Structure

```
div.card.vocab-card#<cardIdPrefix>-<id>  [onclick=toggleCard]
  └── div.card-inner                      [style=transform:rotateY(...)]
        ├── div.card-front
        │     ├── header: word (h3) + phonetic + audio-btn + theme-badge + delete-btn
        │     ├── chinese translation (p)
        │     ├── definition/context (p, line-clamp-2)
        │     ├── difficulty dots (optional)
        │     └── flip hint (optional)
        └── div.card-back
              ├── Synonyms label + tag cloud
              ├── Example label + sentence
              └── flip-back hint
```

### 9.5 Data Adapter Pattern (collection.html)

Since `localStorage` myWords entries lack `pos`/`definition`/`theme`/`difficulty`, `collection.html` uses an adapter function:

```javascript
function adaptMyWord(w) {
  return {
    id: w.id,
    word: w.word,
    chinese: w.chinese || '',
    phonetic: w.phonetic || '',
    audioUrl: w.audioUrl || '',
    synonyms: w.synonyms || [],
    definition: '',                          // not available from reading lookup
    example: '',                             // use contextSentence instead
    contextSentence: w.contextSentence || '',
    contextHtml: highlightWord(w.contextSentence, w.word),  // pre-highlighted
    pos: '', theme: '', difficulty: 0,
  };
}
```

### 7.6 Flip State

Card flip state is stored in `window._vocabCardFlipped` (a `Set` of card IDs). This persists across filter changes within a page session. The `toggleCard()` function toggles membership in this Set and applies inline `rotateY` transform accordingly.

---

## 9. Core Feature: Collection System (个性化生词本与长句收集)

### 9.1 Classification Logic

```javascript
isWord = cleanedText.split(/\s+/).length <= 3
// ≤3 words → saved as "word/phrase"
// >3 words → saved as "sentence"
```

### 9.2 Word Save Flow

```
User clicks "📌 加入收藏" on tooltip
        │
        ▼
  Button shows "⏳ 收集中..."
        │
        ▼
  extractContextSentence(anchorNode):
    Walks up DOM from selection.anchorNode to find closest <p>
    Returns full paragraph text as "context sentence"
        │
        ▼
  enrichWord(word):
    Calls GET /api/dictionary-lookup?word=<word>
    Backend proxies to https://api.dictionaryapi.dev/api/v2/entries/en/<word>
    Returns { phonetic, audioUrl, synonyms[] }
    Gracefully returns null if API 404s or errors
        │
        ▼
  Construct entry object + save to localStorage
        │
        ▼
  Button changes to "✅ 已保存" (disabled, green)
```

### 9.3 Sentence Save Flow

```
User clicks "📌 加入收藏" on tooltip (for text with >3 words)
        │
        ▼
  Button shows "⏳ 收集中..."
        │
        ▼
  matchHighFreqWords(sentence):
    Tokenizes sentence into words
    Cross-references against ieltsVocab[] (loaded from /api/vocabulary on page load)
    Returns [{ word, chinese }] for each match
        │
        ▼
  Construct entry object + save to localStorage
        │
        ▼
  Button changes to "✅ 已保存"
```

### 9.4 localStorage Data Structures

**Key: `ielts_myWords`** — Array of word entries:
```json
[
  {
    "id": 1718123456789,
    "word": "unprecedented",
    "chinese": "前所未有的",
    "phonetic": "/ʌnˈpresɪdentɪd/",
    "audioUrl": "https://api.dictionaryapi.dev/media/pronunciations/en/unprecedented-us.mp3",
    "synonyms": ["unparalleled", "exceptional", "extraordinary"],
    "contextSentence": "The global economy is facing unprecedented challenges as trade tensions continue to escalate.",
    "savedAt": 1718123456789
  }
]
```
- Dedup: by `word` (case-insensitive)
- Max: 100 entries (oldest evicted)
- `audioUrl` may be empty string if API returns no audio
- `phonetic` may be empty string if API returns no phonetics

**Key: `ielts_mySentences`** — Array of sentence entries:
```json
[
  {
    "id": 1718123456790,
    "sentence": "The global economy is facing unprecedented challenges as trade tensions continue to escalate.",
    "chinese": "随着贸易紧张局势持续升级，全球经济正面临前所未有的挑战。",
    "highFreqWords": [
      { "word": "global", "chinese": "全球的" },
      { "word": "economy", "chinese": "经济" }
    ],
    "savedAt": 1718123456790
  }
]
```
- Dedup: by `sentence` (case-insensitive)
- Max: 100 entries
- `highFreqWords` may be empty array if no IELTS vocab matches found

### 9.5 Collection Page (`collection.html`)

- Two tabs: "📝 我的单词" / "📄 我的句子"
- Reads directly from `localStorage` on page load
- **Word cards**: Rendered via shared `VocabCard()` component with 3D flip animation (same UI as vocabulary.html)
  - Data adapter (`adaptMyWord()`) maps localStorage fields → VocabCard props
  - Front: word, phonetic, 🔊 audio button, Chinese translation, context sentence with highlighted word
  - Back: synonym tags, context sentence as example, flip-back hint
  - Delete button (🗑) + saved timestamp on each card
  - Responsive grid: 1→2→3 columns
- **Sentence cards**: Flat cards (no flip) — original text, Chinese translation, matched high-frequency word tags
- Delete button (🗑) on each entry removes and re-renders
- Empty states with CTA to go read articles
- Audio playback via shared `playAudio()` from `js/vocab-card.js`

---

## 10. Page-by-Page Reference

### index.html
- Hero section + **4 feature cards** (Mock Test, Writing, Reading, Vocabulary)
- Navigation: desktop (`hidden sm:flex`) + mobile (`sm:hidden`) — includes **机考模拟** link

### mock-test.html ★ NEW
- Full computer-delivered IELTS Reading mock test simulation
- Left-right split pane with independent scrolling
- Text highlighting tool (select → highlight yellow), 60-min countdown timer with 10min/5min color warnings
- Bottom question navigator with 1-40 numbered blocks, answered/current status indicators
- 13 real Cambridge IELTS 9 Test 1 questions (TRUE/FALSE/NOT GIVEN + Short Answer)
- Submit & review flow with score calculation and correct/incorrect answer display
- Keyboard navigation (Tab, Ctrl+←/→)
- Font size toggle (3 levels), help overlay
- See §4 for full module documentation

### writing.html
- 3 tabs: 评分标准, Simon 写作法, 高分范文拆解
- Content loaded from `/api/band-descriptors`, `/api/methodology`, `/api/essays`
- Rich prose styling (`.prose` class)
- Desktop-only navigation

### reading.html
- 5 article selector buttons at top
- Left panel: article content (`#article-body`) with vocabulary highlights
- Right panel: translation history (`#history-list`) + strategy accordion
- All translation + collection logic in inline script
- Desktop-only navigation

### vocabulary.html
- 288 vocabulary cards rendered via shared `VocabCard()` component (`js/vocab-card.js`)
- CSS 3D flip animation (`.card-inner`, `rotateY(180deg)`) — front: word/pos/theme/phonetic/audio/definition/difficulty; back: synonyms/example
- Filter by theme (6 categories) + difficulty (1-5 stars)
- Audio pronunciation button (🔊) on cards with `audioUrl` — uses shared `playAudio()`
- Responsive grid: 1→2→3→4 columns
- Desktop + mobile navigation

### collection.html
- **My Words tab**: Renders saved words as VocabCard components (same 3D flip UI as vocabulary.html)
  - Data adapter (`adaptMyWord()`) maps localStorage fields → VocabCard props
  - Context sentences displayed with highlighted target word on card front
  - Full example + synonyms on card back (flip to reveal)
  - Delete button + save timestamp on each card
  - Responsive grid: 1→2→3 columns
- **My Sentences tab**: Flat cards with sentence text, Chinese translation, matched high-frequency word tags
- See §6.5 for data flow details
- Desktop + mobile navigation

---

## 11. External API Reference

### MyMemory Translation API
- **URL**: `https://api.mymemory.translated.net/get?q=<text>&langpair=en|zh`
- **Auth**: None (free tier, rate-limited)
- **Response**: `{ responseStatus, responseData: { translatedText, match } }`
- **Proxied via**: `server.js` → `/api/translate` and `netlify/functions/translate.js`
- **Match score**: `match` field indicates translation quality (1.0 = human, <1.0 = machine)

### Free Dictionary API
- **URL**: `https://api.dictionaryapi.dev/api/v2/entries/en/<word>`
- **Auth**: None (open API)
- **Response**: Array of `{ word, phonetic, phonetics: [{ text, audio }], meanings: [{ partOfSpeech, definitions: [{ definition, example, synonyms }], synonyms }] }`
- **Proxied via**: `server.js` → `/api/dictionary-lookup` and `netlify/functions/dictionary-lookup.js`
- **404 handling**: Returns `{ found: false, word }` instead of error
- **Field extraction**: Takes first entry's phonetic text, first audio URL, deduplicated synonyms (max 10)

### Local Dictionary (`data/dictionary.json`)
- 558 English words → Chinese translations
- Flat `{ "word": "translation", ... }` structure
- Used for instant single-word lookup (no network request)
- Case-insensitive matching; tries lowercase, original case, then capitalized

---

## 12. Git History

```
<TBD> Feat: Add official computer-delivered IELTS reading mock interface
fafdbe5 Feat: Add Vocabulary and Sentence collection system with audio and context
bb597e1 Enhance: Upgrade translation engine for full sentences and add loading UI
3bb0546 Fix: 实现划词翻译功能 + 修复词汇页移动端适配
d004640 🚀 Add Netlify deployment support
2c8cfd9 🎉 Initial commit: IELTS Study Portal
```

All commits on `main` branch. Branch is protected only by being private.

---

## 13. Known Limitations & Future TODOs

### Architectural Limitations

| # | Issue | Impact | Suggested Fix |
|---|-------|--------|---------------|
| 1 | **localStorage is device-local** | User's collection does not sync across devices/browsers | Add optional cloud sync (Firebase, Supabase) or export/import JSON |
| 2 | **No user authentication** | All collection data is tied to the browser, not the user | Add login + backend storage |
| 3 | **MyMemory API rate limits** | Free tier has undocumented rate limits; heavy use may get throttled | Add queue/retry logic or switch to a paid translation API |
| 4 | **No offline support** | Pages require CDN (Tailwind) and API access to function | Add Service Worker for offline caching |
| 5 | **558-word dictionary is static** | New words not in dictionary always require API call | Periodically expand `dictionary.json` from saved words |
| 6 | **No automated testing** | Zero test coverage — all testing is manual | Add Playwright or Cypress E2E tests |
| 7 | **Legacy `api/` directory** | Contains Vercel-style serverless functions from early deployment attempt (abandoned) | Remove or repurpose if switching to Vercel |
| 8 | **No TypeScript** | No type checking; runtime errors possible | Convert to TypeScript if project grows |
| 9 | **Audio autoplay may be blocked** | Browsers block `Audio.play()` without prior user gesture; fallback is silent | Add visible "Click to play" fallback UI |
| 10 | **vocabulary.html lacks mobile nav writing link** | Mobile nav omits "写作" link (regression from earlier fix) | Add back writing link to mobile nav |

### No Explicit TODOs in Code
A full-text search for `TODO`, `FIXME`, `HACK`, `XXX` returned zero results. All known issues are documented in this section only.

---

## 14. Development Workflow

### Local Development
```bash
cd IELTS_Study_Portal
node server.js
# Server starts at http://localhost:3456
# All 5 pages + 8 API endpoints available
```

### Deploy to Production
```bash
git add .
git commit -m "Descriptive message"
git push
# Netlify auto-detects push to main, builds in ~30 seconds
# Verify: curl https://elaborate-duckanoo-d25740.netlify.app/api/translate?text=test
```

### Adding a New API Route
1. Add route handler in `server.js` (local dev)
2. Create corresponding `netlify/functions/<name>.js` (production)
3. If serving static JSON, add entry to `API_ROUTES` in `server.js` and create matching Netlify function
4. Test locally: `curl http://localhost:3456/api/<name>`
5. Push and verify production

### Adding a New Page
1. Create `<name>.html` in project root
2. Include Tailwind CDN + brand config (copy from any existing page)
3. Add navigation link to all 5 pages (desktop + mobile where applicable)
4. Test locally at `http://localhost:3456/<name>.html`
5. Push — Netlify serves it automatically (no build step)

---

## 15. Key Configuration Values

| Config | Value | Location |
|--------|-------|----------|
| Local port | `3456` | `server.js:6` |
| Netlify site name | `elaborate-duckanoo-d25740` | Auto-generated by Netlify |
| Tailwind brand colors | `#f0f4f8` → `#102a43` (10 shades) | Inline `<script>` in every `.html` |
| Translation debounce | `400ms` | `reading.html` (in `setTimeout`) |
| Collection max entries | `100` per type | `reading.html` (in `saveMyWords`/`saveMySentences`) |
| History max entries | `20` | `reading.html` (in `addToHistory`) |
| Dictionary entries | `558` | `data/dictionary.json` |
| Vocabulary entries | `288` | `data/vocabulary.json` |
| Reading articles | `5` | `data/reading-articles.json` |
| Sample essays | `3` | `data/essays.json` |
| Mock test timer | `3600s` (60 min) | `mock-test.html` (`TEST_TIME`) |
| Mock test questions | `13` (MVP) | `data/mock-test-1.json` |
| Timer warning thresholds | `600s` / `300s` | `mock-test.html` (`updateTimer`) |

---

*End of handoff document. If you're a new AI agent, start by reading this file, then explore any area you need to modify.*
