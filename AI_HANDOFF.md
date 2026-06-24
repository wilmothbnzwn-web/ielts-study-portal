# AI Handoff Document — IELTS Study Portal

> **READ THIS FIRST** if you are a new AI agent taking over this project.
> Every architectural decision, data schema, API route, storage key, and known limitation is documented below.
> **Breaking any contract described here WILL cause production failures.**

**Last updated:** 2026-06-24 (vocabulary Deck System refactor)
**Total commits on `main`:** upcoming
**Production URL:** `https://elaborate-duckanoo-d25740.netlify.app`
**GitHub remote:** `https://github.com/wilmothbnzwn-web/ielts-study-portal.git`
**BaaS Platform:** Supabase (PostgreSQL + Auth)

---

## 1. Project Overview

| Field | Value |
|-------|-------|
| **Purpose** | IELTS Academic Reading & Writing self-study portal for Chinese-speaking learners |
| **Audience** | Chinese students preparing for IELTS Academic (雅思 A 类) |
| **Language** | Mixed Chinese/English UI; English-only test content |
| **Deployment** | Netlify static site + serverless functions (auto-deploy on `git push` to `main`) |
| **Local dev** | Node.js `http` server on port `3456` (run `node server.js` or `npm start`) |
| **Architecture** | Pure HTML/CSS/JS frontend + Node.js static server + Netlify serverless functions for API |
| **CSS Framework** | Tailwind CSS v3 CDN (`https://cdn.tailwindcss.com`) with inline brand color config |
| **Database** | Supabase PostgreSQL (formerly: static JSON files) — user data is cloud-backed, multi-tenant via RLS |
| **State** | Supabase Auth session + Supabase DB (formerly: browser `localStorage` only) — multi-device sync, no server-side state |
| **Auth** | Supabase Auth — email/password sign-up/sign-in, JWT session tokens, auto-refresh |

### Git History (most recent first)

```
f6ed21b Data: Batch OCR pipeline processes 16 prediction PDFs, expands reading library to 115 tests (925 questions)
abd6610 Docs: update AI_HANDOFF.md with commit hash and test counts
ea2e106 Data: OCR-extract 4 reading tests from 我预测阅读机经 阅读17.pdf and inject
5349969 Docs: update AI_HANDOFF.md with commit hash
77bff44 Data: Auto-parse and inject 5 IELTS reading mocks into dynamic library
2d48acd Docs: update AI_HANDOFF.md with commit hash c961392
c961392 Feat: Add Reading Library list view and dynamic routing to mock test interface
81719d0 Docs: fix AI_HANDOFF.md git history and section numbering
7c033f5 Feat: Add official computer-delivered IELTS reading mock interface
eaf9bda Fix: Resolve text overflow bug in VocabCard component
b36e951 Refactor: Extract VocabCard component and unify UI in My Collection
1fd824e Data: Expand IELTS vocabulary database with 200+ academic words
c3d1c09 Docs: Create AI handoff document for context continuity
fafdbe5 Feat: Add Vocabulary and Sentence collection system with audio and context
bb597e1 Enhance: Upgrade translation engine for full sentences and add loading UI
```

All commits on `main` branch. No other branches exist.

---

## 2. Tech Stack & File Structure

### Core Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | Vanilla HTML5 + CSS3 + ES6 JavaScript | Zero build step, instant Netlify deploy |
| **CSS** | Tailwind CSS v3 CDN (`<script src="https://cdn.tailwindcss.com">`) | Utility-first, responsive, no PostCSS config |
| **Icons** | Native emoji (no icon library) | Zero dependencies, universally rendered |
| **Fonts** | System font stack (`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto...`) | No FOUT, no external requests |
| **Audio** | Web Speech API (`speechSynthesis`) | Built-in TTS, no external audio files |
| **Translation** | MyMemory API (free tier, `https://api.mymemory.translated.net/get`) | No API key needed |
| **Routing** | `URLSearchParams` (query-string based) | No SPA framework needed |
| **Server** | Node.js `http` module (vanilla, no Express) | Minimal, 0 dependencies |
| **Serverless** | Netlify Functions (AWS Lambda under the hood) | Auto-deploy, free tier sufficient |
| **Python Scripts** | Python 3.14 + Tesseract OCR + pdf2image + pytesseract | OCR pipeline for batch PDF processing |

### Full File Tree (as of 2026-06-17)

```
IELTS_Study_Portal/
├── .gitignore                        # Ignores: node_modules/, .DS_Store, *.backup.*, scripts/ocr_output/
├── .netlify/
│   ├── netlify.toml                  # (legacy)
│   ├── state.json
│   └── functions/                    # Pre-built function zips (legacy)
├── netlify.toml                      # Netlify config: build dir, function dir, API redirects
├── vercel.json                       # Vercel redirects (unused, kept for portability)
├── package.json                      # npm metadata, scripts: { start, dev }
├── server.js                         # Local dev server (Node http, port 3456)
│
├── index.html                        # Home page (IELTS overview dashboard)
├── reading.html                      # Reading practice page (articles + translation + Supabase save)
├── reading-library.html              # Reading test library (card grid, 115 tests, topic filter, search)
├── mock-test.html                    # Computer-delivered IELTS reading mock test (auth-protected)
├── writing.html                      # Writing practice page (essay analysis)
├── vocabulary.html                   # ★ Vocabulary Deck Library (/vocab): generated deck cover grid
├── vocab-deck.html                   # ★ Flashcard Study Mode (/vocab/deck/<id>): one VocabCard at a time
├── collection.html                   # "My Collection" page (Supabase-backed, auth-protected)
├── login.html                        # ★ Sign-in page (email/password, Supabase Auth)
├── register.html                     # ★ Registration page (email/password, Supabase Auth)
│
├── js/
│   ├── vocab-card.js                 # Shared VocabCard component (3D flip, audio/TTS, theme colors)
│   ├── vocab-decks.js                # ★ Deck grouping/chunking logic for vocabulary.html + vocab-deck.html
│   ├── auth-store.js                 # ★ Supabase client + pub/sub auth state + session recovery
│   ├── auth-guard.js                 # ★ Route guard: redirects to login if not authenticated
│   ├── navbar.js                     # ★ Shared navbar with reactive user menu (login/logout)
│   ├── db.js                         # ★ Supabase CRUD: words + sentences (replaces localStorage)
│   └── env.js                        # ★ Dynamically served: SUPABASE_URL + SUPABASE_ANON_KEY
│
├── data/
│   ├── reading_tests.json            # ★ CORE: 115 reading tests, 925 questions (1.18 MB)
│   ├── vocabulary.json               # 288 academic vocabulary entries
│   ├── dictionary.json               # 558 word→definition lookups
│   ├── essays.json                   # 3 sample IELTS essays with band analysis
│   ├── reading-articles.json         # 5 reading articles for practice page
│   ├── methodology.json              # 3 methodology entries
│   ├── band-descriptors.json         # IELTS band score descriptors
│   └── mock-test-1.json              # (legacy mock test, superseded by reading_tests.json)
│
├── api/                              # Local API routes (served by server.js in dev)
│   ├── band-descriptors.js
│   ├── essays.js
│   ├── methodology.js
│   ├── reading-articles.js
│   └── vocabulary.js
│
├── netlify/functions/                # Netlify serverless functions (production API)
│   ├── env.js                        # ★ Serves /js/env.js (SUPABASE_URL + SUPABASE_ANON_KEY)
│   ├── band-descriptors.js
│   ├── essays.js
│   ├── methodology.js
│   ├── reading-articles.js
│   ├── reading-tests.js              # ★ Serves reading_tests.json
│   ├── vocabulary.js
│   ├── dictionary.js
│   ├── dictionary-lookup.js
│   ├── mock-test-1.js                # (legacy)
│   └── translate.js                  # Translation proxy (MyMemory API)
│
├── .env.local                        # ★ Supabase credentials (git-ignored)
├── netlify.toml                      # ★ Netlify config with /js/env.js rewrite rule
└── scripts/                          # ★ Python data pipeline scripts
    ├── supabase_migration.sql        # ★ SQL to create user_words + user_sentences tables + RLS
    ├── batch_ocr_pipeline.py         # Batch OCR: scan PDFs → extract text (Tesseract)
    ├── inject_from_ocr.py            # OCR text → structured test JSON → inject into reading_tests.json
    ├── ocr_pipeline_phase1.py        # Original single-PDF OCR script (superseded by batch version)
    ├── inject_tests.py               # First injection script (5 LLM-generated tests)
    ├── inject_ocr_tests.py           # Manual injection script (4 tests from 阅读17)
    ├── generate-vocabulary.js        # Node script to generate vocabulary.json
    └── ocr_output/                   # ★ OCR raw output (~2 MB, .txt + .json per PDF)
        ├── _batch_summary.json       # Batch processing summary
        ├── 阅读18_新版_集合_pdf.txt
        ├── 阅读19_新版_-全文_pdf.txt
        ├── 阅读20_新版_-1_19_pdf.txt
        ├── ... (16 PDFs total)
        └── 阅读38_pdf.txt
```

### Key Architecture Decisions

1. **No build step.** All HTML pages are self-contained. Tailwind is loaded via CDN `<script>`. This means a `git push` is the entire deploy pipeline — Netlify serves files as-is.

2. **API duality.** Local dev uses `server.js` to serve static files + API routes. Production uses Netlify Functions (in `/netlify/functions/`). Both serve the same JSON files from `/data/`. The `netlify.toml` redirects `/api/*` → `/.netlify/functions/:splat`.

3. **Dynamic mock test routing.** `reading-library.html` links to `mock-test.html?testId=<id>`. The mock test page reads `URLSearchParams`, fetches `/api/reading-tests`, finds the matching test by `id`, and renders it.

4. **Compatibility wrapper.** `mock-test.html` normalizes old test format (`flat` questions array) to new format (`passages[]` array with nested questions) at lines ~520-545.

5. **Vocabulary deck routing.** `server.js` maps `/vocab` → `vocabulary.html` and `/vocab/deck/<id>` → `vocab-deck.html`. Production uses matching Netlify rewrites in `netlify.toml`.

---

## 2b. Authentication & User System (Supabase BaaS)

### Architecture Overview

The project migrated from localStorage to Supabase BaaS for multi-user support. All user data (words, sentences) is now stored in Supabase PostgreSQL tables with Row-Level Security (RLS). Authentication is handled by Supabase Auth (email/password).

### Key Architectural Decisions

1. **Zero-build integration.** Supabase SDK (`@supabase/supabase-js@2.45.0`) is loaded via CDN import map (esm.sh). No npm install, no bundler. This preserves the project's zero-build philosophy.

2. **Environment variable injection.** `SUPABASE_URL` and `SUPABASE_ANON_KEY` must reach the browser. Local dev uses `server.js` to read `.env.local` and serve a dynamic ES module at `/js/env.js`. Production uses a Netlify Function (`netlify/functions/env.js`) + rewrite rule in `netlify.toml`.

   ```
   Browser:  import { SUPABASE_URL } from '/js/env.js'
                    │
   Local dev:       server.js reads .env.local → serves JS module
   Production:       Netlify redirect → /.netlify/functions/env → process.env
   ```

3. **Pub/sub auth store.** `js/auth-store.js` provides a vanilla JS reactive store. All pages import the same module — ES module caching ensures a singleton Supabase client and shared auth state.

4. **Bridge pattern for inline scripts.** Existing pages use inline `<script>` blocks (not modules), which can't use `import`. A thin `<script type="module">` bridge imports from `js/db.js` and assigns to `window._db`, making Supabase functions available to legacy inline code.

### New Files (Supabase Migration)

| File | Purpose |
|------|---------|
| `js/auth-store.js` | Supabase client singleton, pub/sub auth state store, `initAuth()` session recovery |
| `js/auth-guard.js` | Route guard: redirects unauthenticated users to `/login.html?redirect=...` |
| `js/navbar.js` | Shared navbar with reactive user menu (login/register or email/logout) |
| `js/db.js` | Supabase CRUD: `getMyWords`, `saveMyWords`, `deleteWord`, `getMySentences`, `saveMySentences`, `deleteSentence` |
| `login.html` | Sign-in page (brand-colored, academic minimalist style) |
| `register.html` | Registration page (matching style) |
| `netlify/functions/env.js` | Netlify Function: serves `/js/env.js` in production |
| `scripts/supabase_migration.sql` | SQL to create tables + RLS policies in Supabase |

### Config Files

| File | Purpose |
|------|---------|
| `.env.local` | `SUPABASE_URL` + `SUPABASE_ANON_KEY` (git-ignored) |
| `netlify.toml` | Rewrite `/js/env.js` → `/.netlify/functions/env` |

### Module Loading Order

All HTML pages load modules like this:

```html
<script type="importmap">
{ "imports": { "@supabase/supabase-js": "https://esm.sh/@supabase/supabase-js@2.45.0" } }
</script>
<script type="module" src="/js/auth-store.js"></script>
```

Dependency graph (linear, no cycles):
```
env.js (dynamically served) ← auth-store.js ← db.js
                                           ← auth-guard.js
                                           ← navbar.js
```

### Route Protection

- **Collection page** (`collection.html`): Requires auth. Loads `auth-guard.js` → redirects to login if not signed in.
- **Mock test** (`mock-test.html`): Requires auth. Loads `auth-guard.js` → redirects to login.
- **Reading page** (`reading.html`): No guard — articles are public. Save button shows "请先登录" if not authenticated.
- **All other pages**: Public. Load `navbar.js` for the user menu but no guard.

### Supabase Database Tables (PostgreSQL + RLS)

**`public.user_words`:**
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | gen_random_uuid() |
| user_id | UUID FK→auth.users | ON DELETE CASCADE |
| word | TEXT NOT NULL | |
| chinese | TEXT | Default '' |
| phonetic | TEXT | Default '' |
| audio_url | TEXT | Default '' |
| synonyms | TEXT | JSON array as string |
| context_sentence | TEXT | Default '' |
| saved_at | TIMESTAMPTZ | Default now() |

**`public.user_sentences`:**
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | gen_random_uuid() |
| user_id | UUID FK→auth.users | ON DELETE CASCADE |
| sentence | TEXT NOT NULL | |
| chinese | TEXT | Default '' |
| high_freq_words | TEXT | JSON array as string |
| saved_at | TIMESTAMPTZ | Default now() |

**RLS Policies:** Users can SELECT/INSERT/DELETE/UPDATE only rows where `auth.uid() = user_id`.

### Column Mapping (JS camelCase ↔ DB snake_case)

`db.js` handles all mapping:
- `audioUrl` ↔ `audio_url`
- `contextSentence` ↔ `context_sentence`
- `highFreqWords` ↔ `high_freq_words`
- `savedAt` ↔ `saved_at`
- `synonyms` and `highFreqWords` are serialized as JSON strings in TEXT columns

---

## 3. Data Schemas (THE CONTRACT — DO NOT BREAK)

### 3.1 reading_tests.json — The Core Database

**File:** `data/reading_tests.json` (1.18 MB, 115 tests, 925 questions)

```json
{
  "tests": [
    {
      "id": "string (unique, kebab-case, e.g. 'cam9-test1' or '18-pdf-p2')",
      "title": "string (human-readable, 20-80 chars)",
      "topic": "string (MUST be one of: 'Science', 'Environment', 'History', 'Economics', 'Sociology', 'Technology')",
      "source": "string (e.g. 'Cambridge IELTS 9 Test 1 Passage 1' or 'IELTS Reading Prediction — 阅读19 Passage 2')",
      "difficulty": "integer (1-5, where 1=easiest, 5=hardest. Most tests are 3.)",
      "totalTime": "integer (seconds, typically 1200 for 20-min passages, 3600 for full tests)",
      "wordCount": "integer (approximate word count of passageText, range 500-3300)",
      "questionCount": "integer (number of questions, range 1-13 per passage)",
      "passageText": "string (HTML paragraphs wrapped in <p>...</p> tags, NO outer wrapper div)",
      "questions": [
        {
          "id": "integer (sequential within test, starting at 1)",
          "type": "string (MUST be one of: 'true_false_not_given' | 'short_answer')",
          "questionText": "string (the question itself, 20-300 chars)",
          "options": ["TRUE", "FALSE", "NOT GIVEN"],  // ONLY for true_false_not_given type
          "correctAnswer": "integer | string (for TFN: 0=TRUE, 1=FALSE, 2=NOT GIVEN; for short_answer: answer string)",
          "wordLimit": "integer (OPTIONAL, only for short_answer type, e.g. 3 means 'NO MORE THAN THREE WORDS')"
        }
      ]
    }
  ]
}
```

**CRITICAL RULES:**
- `topic` values are **EXACT** strings. The CSS classes in `reading-library.html` are generated as `topic-<lowercase>`. Adding a new topic requires: (1) adding the CSS class `.topic-<name>`, (2) adding an entry in `TOPIC_CONFIG` in `reading-library.html`.
- `type` MUST be `"true_false_not_given"` or `"short_answer"`. The mock test renderer has explicit branching for these two types. Unknown types WILL break the mock test UI.
- `passageText` MUST be valid HTML with `<p>...</p>` wrapping each paragraph. It is injected via `innerHTML`.
- `correctAnswer` for TFN: `0` = TRUE (first option), `1` = FALSE (second), `2` = NOT GIVEN (third).
- `id` fields must be UNIQUE across all tests. Duplicate IDs will cause injection failures.

### 3.2 vocabulary.json

**File:** `data/vocabulary.json` (288 entries)

```json
[
  {
    "id": "integer",
    "word": "string (the headword)",
    "pos": "string (part of speech: 'noun', 'verb', 'adjective', 'adverb', 'phrase')",
    "chinese": "string (Chinese translation)",
    "synonyms": ["string array (3-5 synonyms)"],
    "definition": "string (English definition, 1-2 sentences)",
    "example": "string (IELTS-context example sentence)",
    "theme": "string (one of ~15 theme labels, e.g. 'Technology & Society', 'Economy & Trade')",
    "difficulty": "integer (1-5)"
  }
]
```

**Theme label → CSS class mapping** is defined in `js/vocab-card.js` in the `THEME_COLORS` object. Adding a new theme requires adding a corresponding CSS class there.

### 3.3 dictionary.json

**File:** `data/dictionary.json` (558 entries)

```json
{
  "word": "string (definition, 50-300 chars)",
  ...
}
```

Simple word→definition map. Used by the translation/glossary feature in `reading.html`.

### 3.4 essays.json

**File:** `data/essays.json` (3 entries)

```json
[
  {
    "id": "integer",
    "title": "string",
    "question": "string (the essay prompt)",
    "type": "string (e.g. 'Opinion', 'Discussion')",
    "band": "integer (overall band score)",
    "ccBand": "integer (Coherence & Cohesion band)",
    "lrBand": "integer (Lexical Resource band)",
    "body": "string (HTML-formatted essay text with <p>, <strong>, <em> tags)",
    "ccAnalysis": "string (HTML analysis of cohesion)",
    "lrAnalysis": "string (HTML analysis of vocabulary)"
  }
]
```

### 3.5 reading-articles.json, methodology.json, band-descriptors.json

These are smaller supporting data files. See them directly for structure.

### 3.6 VocabCard Component Contract

**File:** `js/vocab-card.js`

```javascript
// Usage:
VocabCard(wordData, options)
// wordData: object matching vocabulary.json entry schema (see §3.2)
// options: { showCollectionActions?: boolean }
// Returns: HTML string

// Expected wordData shape:
{
  id: number,
  word: string,
  pos: string,
  chinese: string,
  synonyms: string[],
  definition: string,
  example: string,
  theme: string,      // MUST match a key in THEME_COLORS
  difficulty: number   // 1-5
}
```

---

## 4. State Management & Storage (Supabase)

**All user data is stored in Supabase PostgreSQL.** There is NO localStorage usage for user content. Auth sessions are managed by Supabase Auth (refresh token in localStorage, handled automatically by the SDK).

### Supabase Database (replaces localStorage)

| Old localStorage Key | New Supabase Table | Operations |
|----------------------|--------------------|------------|
| `ielts_myWords` | `public.user_words` (RLS-protected) | `getMyWords()`, `saveMyWords([entries])`, `deleteWord(id)` |
| `ielts_mySentences` | `public.user_sentences` (RLS-protected) | `getMySentences()`, `saveMySentences([entries])`, `deleteSentence(id)` |

**Code contract** (from `js/db.js`):
```javascript
// All async — must use await
const words = await window._db.getMyWords();
await window._db.saveMyWords([{ word, chinese, ... }]);
await window._db.deleteWord(id);

const sentences = await window._db.getMySentences();
await window._db.saveMySentences([{ sentence, chinese, ... }]);
await window._db.deleteSentence(id);
```

**Bridge pattern:** Inline (non-module) scripts access these via `window._db`, set up by a `<script type="module">` bridge. Functions are auto-deduplicated (ilike match on word/sentence for the same user).

### Auth State (pub/sub store)

- `authStore.user` — current Supabase user object (or null)
- `authStore.isAuthenticated` — boolean
- `authStore.subscribe(fn)` — reactive listener, returns unsubscribe function
- `initAuth()` — recovers session from Supabase on page load

### Session-only State (in-memory, not persisted — unchanged)

| State | Location | Notes |
|-------|----------|-------|
| Mock test timer | `mock-test.html` (variable `timeRemaining`) | Resets on page reload |
| User answers | `mock-test.html` (object `userAnswers`) | NOT persisted; lost on page close |
| Current question index | `mock-test.html` (variable `currentQuestionIndex`) | For highlight tracking |
| Translation history | `reading.html` (array `lookupHistory`, max 20) | Session-only, not persisted |

---

## 5. Automated Pipelines

### 5.1 OCR Batch Pipeline

**Purpose:** Extract text from scanned IELTS reading prediction PDFs (我预测阅读机经) and convert to structured test JSON.

**Source PDFs location:** `/Users/zzzzhangjintao/Desktop/IELTS_Organized_Library/02_阅读专项精读库_Reading_by_Topic/07_Reading_Methodology_and_Skills/我预测阅读机经库/`

**Scripts involved:**

#### Step 1: `scripts/batch_ocr_pipeline.py`
```
python3 scripts/batch_ocr_pipeline.py [--dry-run] [--max-pdfs N] [--dpi 200] [--max-pages 55]
```
- Scans the 我预测阅读机经库 directory for PDFs
- Priority sorting: 新版+全文 > 新版 > 全文 > 新 > rest
- Skips already-OCR'd PDFs (checks for existing output >10KB)
- Runs Tesseract OCR (lang=`eng+chi_sim`, DPI=200 default) on pages 7-61 of each PDF
- Saves raw text to `scripts/ocr_output/<pdf_label>.txt` and `.json`
- Saves batch summary to `scripts/ocr_output/_batch_summary.json`
- **Error handling:** Per-PDF try/catch; one PDF crash does NOT abort the batch

#### Step 2: `scripts/inject_from_ocr.py`
```
python3 scripts/inject_from_ocr.py [--dry-run] [--min-chars 30000]
```
- Reads all `.txt` OCR output files in `scripts/ocr_output/`
- State-machine parser detects passage boundaries (lettered paragraphs A-I) and question sections
- Quality filters: min 500 words, min 6 questions, title >55% alphabetic
- Max 4 passages extracted per PDF (configurable: `MAX_TESTS_PER_PDF`)
- Auto-generates metadata: title, topic (keyword matching), difficulty (text complexity heuristic)
- Appends new tests to `data/reading_tests.json`
- Creates `.backup.*` before writing
- Skips already-injected test IDs and previously-processed sources (阅读17)

**Dependencies:**
```bash
brew install tesseract poppler
pip3 install pdf2image pytesseract --break-system-packages
```

**Known limitations:**
- OCR accuracy is ~80-85% for English text on these scanned PDFs
- Questions are auto-generated as placeholder TFN (correctAnswer defaults to 0/TRUE) — manual answer verification needed
- Some passage titles contain OCR noise (garbled characters)
- Large PDFs (190MB+) may take 3-5 minutes each to OCR
- The parser may fail to separate passages cleanly when PDF layout is irregular

### 5.2 Manual Test Injection (Legacy)

- `scripts/inject_tests.py` — Injects 5 LLM-generated tests (cam7-test1, cam11-test3, cam8-test1, cam10-test1, cam15-test1)
- `scripts/inject_ocr_tests.py` — Contains 4 hand-crafted test objects from 阅读17.pdf (predict17-p1 through predict17-p4)

---

## 6. Topic System & UI Configuration

### Topic Tags (used in reading-library.html)

The topic tag CSS classes are defined inline in `reading-library.html:46-51`:

| Topic | CSS Class | Icon | Background | Text Color |
|-------|-----------|------|------------|------------|
| Science | `topic-science` | 🔬 | `#dbeafe` (blue-100) | `#1e40af` (blue-800) |
| Environment | `topic-environment` | 🌍 | `#d1fae5` (green-100) | `#065f46` (green-800) |
| History | `topic-history` | 📜 | `#fef3c7` (yellow-100) | `#92400e` (yellow-800) |
| Economics | `topic-economics` | 💼 | `#fce7f3` (pink-100) | `#9d174d` (pink-800) |
| Sociology | `topic-sociology` | 👥 | `#ede9fe` (purple-100) | `#5b21b6` (purple-800) |
| Technology | `topic-technology` | ⚙️ | `#ffedd5` (orange-100) | `#9a3412` (orange-800) |

**To add a new topic, you MUST edit:**
1. `reading-library.html` — add `.topic-<name>` CSS class AND entry in `TOPIC_CONFIG` object
2. `scripts/inject_from_ocr.py` — add keywords to `TOPIC_KEYWORDS` dict

### Brand Colors (Tailwind config, inline in every .html `<script>`)

```javascript
tailwind.config = {
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f4f8', 100: '#d9e2ec', 200: '#bcccdc', 300: '#9fb3c8',
          400: '#829ab1', 500: '#627d98', 600: '#486581', 700: '#334e68',
          800: '#243b53', 900: '#102a43',
        }
      }
    }
  }
}
```

### Timer Configuration (mock-test.html)

| Config | Value | Location |
|--------|-------|----------|
| `TEST_TIME` | `3600` (60 min) | `mock-test.html:480` |
| Warning threshold | `600s` (10 min) | CSS class `.warning` triggers |
| Danger threshold | `300s` (5 min) | CSS class `.danger` triggers |

### Vocabulary Deck System

**Files:** `vocabulary.html`, `vocab-deck.html`, `js/vocab-decks.js`, `js/vocab-card.js`

The old flat vocabulary grid has been replaced by a deck-based study system:

- `/vocab` renders the **词书大厅 / Deck Library** with CSS Grid cover cards.
- `/vocab/deck/<id>` renders **Flashcard Study Mode**, showing one reused `VocabCard` at a time.
- Prev/Next controls update the current card and progress bar. Prev is disabled on the first card; Next is disabled on the final card.
- `VocabCard` still handles 3D flip, synonyms, IELTS example sentences, theme styling, and pronunciation. Static vocabulary entries without `audioUrl` now fall back to Web Speech API TTS.

**Deck generation contract (`js/vocab-decks.js`):**

1. If a word has `source`, `book`, or `origin`, group by that source label.
2. Otherwise group the current static vocabulary by broad IELTS themes:
   - `Academic`: Academic / Education / Research / Knowledge / Science
   - `Business`: Economy / Trade / Finance / Business
   - `Society`: Technology / Environment / Social / Politics / Governance / Law / Policy / Culture / Health / Medicine
3. Each group is split with `VOCAB_DECK_TARGET_SIZE = 24`, producing 20-30 word decks for the current 288-word dataset.
4. Current output: 14 decks total, each 20-22 words.

### Component: VocabCard

**File:** `js/vocab-card.js`
**THEME_COLORS mapping:** 15 theme labels → Tailwind background/text color classes
**Behavior:** 3D card flip on click (front: word/chinese; back: definition/example/synonyms), audio TTS button

---

## 7. API Routes

### Local Dev (server.js, port 3456)

| Route | Data File |
|-------|-----------|
| `GET /api/reading-tests` | `data/reading_tests.json` |
| `GET /api/vocabulary` | `data/vocabulary.json` |
| `GET /api/dictionary` | `data/dictionary.json` |
| `GET /api/essays` | `data/essays.json` |
| `GET /api/reading-articles` | `data/reading-articles.json` |
| `GET /api/methodology` | `data/methodology.json` |
| `GET /api/band-descriptors` | `data/band-descriptors.json` |
| `GET /api/mock-test-1` | `data/mock-test-1.json` (legacy) |

### Production (Netlify Functions)

Same routes, served by corresponding `.js` files in `netlify/functions/`. The `netlify.toml` redirects all `/api/*` requests to `/.netlify/functions/:splat`.

### Translation API (MyMemory)

```
GET https://api.mymemory.translated.net/get?q=<text>&langpair=en|zh-CN
```
Proxied through `netlify/functions/translate.js` in production. Called from `reading.html` with 400ms debounce.

---

## 8. Mock Test Interface Architecture

**File:** `mock-test.html`

### Flow
1. Page loads → reads `?testId=<id>` from URL
2. Fetches `GET /api/reading-tests`
3. Finds test by `id`
4. Checks for `passages[]` array (new format) vs flat `questions[]` (old format)
5. Renders: left pane = passage text (`passageText` via `innerHTML`), right pane = questions
6. Timer starts at `test.totalTime` seconds (or `TEST_TIME=3600` default)
7. User answers saved to `userAnswers` object (in-memory, NOT persisted)

### Question Rendering
- `true_false_not_given`: 3-button group (TRUE / FALSE / NOT GIVEN), single-select
- `short_answer`: text `<input>` with `wordLimit` placeholder

### Compatibility Wrapper (~line 520-545)
Old tests with flat `questions[]` are wrapped into `passages: [{ passageText, questions }]` at runtime.

---

## 9. Key Configuration Values

| Config | Value | Location |
|--------|-------|----------|
| Local port | `3456` default, override with `PORT=<port>` | `server.js:6` |
| Netlify site name | `elaborate-duckanoo-d25740` | Auto-assigned by Netlify |
| Tailwind brand colors | `#f0f4f8` → `#102a43` (10 shades) | Inline `<script>` in every `.html` |
| Translation debounce | `400ms` | `reading.html` |
| Collection max entries | `100` per type | `reading.html`, `collection.html` |
| History max entries | `20` | `reading.html` |
| Dictionary entries | `558` | `data/dictionary.json` |
| Vocabulary entries | `288` | `data/vocabulary.json` |
| Reading articles | `5` | `data/reading-articles.json` |
| Sample essays | `3` | `data/essays.json` |
| Mock test timer default | `3600s` (60 min) | `mock-test.html` (`TEST_TIME`) |
| Reading tests | `115` (Environment×31, Sociology×23, Science×22, Economics×22, History×9, Technology×8) | `data/reading_tests.json` |
| Total questions | `925` across 115 tests | `data/reading_tests.json` |
| OCR DPI | `200` | `scripts/batch_ocr_pipeline.py` |
| OCR language | `eng+chi_sim` | `scripts/batch_ocr_pipeline.py` |

---

## 10. Instructions for the Next AI Agent

### ⚠️ WARNINGS — Read Before Making ANY Changes

1. **DO NOT change the data schemas** in `data/reading_tests.json` without updating every consumer: `mock-test.html` (test rendering), `reading-library.html` (card display), `netlify/functions/reading-tests.js` (API serverless function), and `scripts/inject_from_ocr.py` (injection pipeline).

2. **DO NOT add new question types** (`type` field) without adding render logic in `mock-test.html` (~line 580-620). The UI has explicit branching for `true_false_not_given` and `short_answer` only.

3. **DO NOT modify the Supabase table schemas** (`user_words`, `user_sentences`) without updating `js/db.js` (column mapping) and `scripts/supabase_migration.sql` (migration reference). The RLS policies are critical — without them, users could see each other's data.

4. **DO NOT remove localStorage key reading code** if users may have existing data. Consider adding a one-time migration button on collection.html that reads old `ielts_myWords`/`ielts_mySentences` from localStorage, calls `saveMyWords()`/`saveMySentences()`, then clears localStorage.

5. **DO NOT remove the compatibility wrapper** in `mock-test.html:520-545` — some older tests may still use the flat format.

5. **DO NOT break the topic system** — `topic` values in JSON MUST exactly match keys in `TOPIC_CONFIG` in `reading-library.html`. Adding a topic requires changes in TWO files.

6. **DO NOT add build steps** — the project is deliberately zero-build. If you add TypeScript/Sass/bundling, the Netlify deploy will break.

7. **DO NOT replace Tailwind CDN** with a custom build unless you also set up a full build pipeline. The CDN approach is intentional for simplicity.

8. **DO NOT push `scripts/ocr_output/` or `*.backup.*` files** to the repo — they are large and unnecessary for the site.

### ✅ Recommended Practices

- **Test locally first:** `node server.js` → visit `http://localhost:3456` before pushing.
- **Validate JSON:** Always run `python3 -c "import json; json.load(open('data/reading_tests.json'))"` after editing the test database.
- **Backup before injection:** The `inject_from_ocr.py` script auto-creates `.backup.*` files before writing.
- **Match existing code style:** The codebase uses vanilla JS (no jQuery), emoji for icons, Chinese for UI labels mixed with English for content.
- **Read `mock-test.html` thoroughly** before touching it — it's the most complex file (~850 lines, timer logic, question rendering, highlight tracking).

### 🔧 Quick Start Commands

```bash
# === FIRST-TIME SETUP ===
# 1. Create a Supabase project at https://app.supabase.com
# 2. Get your project URL and anon key from: Settings > API
# 3. Create .env.local in project root:
#    SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
#    SUPABASE_ANON_KEY=eyJhbGciOi...
# 4. Run the SQL migration in Supabase SQL Editor:
#    Copy scripts/supabase_migration.sql → paste into SQL Editor → Run
# 5. (Optional) Disable email confirmation for dev:
#    Supabase dashboard > Authentication > Settings > Auth Settings
#    Toggle "Confirm email" to OFF

# Local dev
cd /Users/zzzzhangjintao/.claude/tt.1/IELTS_Study_Portal
node server.js
# → http://localhost:3456

# Verify Supabase config is injected
curl -s http://localhost:3456/js/env.js
# Should output: export const SUPABASE_URL = "..."; export const SUPABASE_ANON_KEY = "...";

# Validate test database
python3 -c "
import json
with open('data/reading_tests.json') as f:
    db = json.load(f)
print(f'{len(db[\"tests\"])} tests, {sum(t[\"questionCount\"] for t in db[\"tests\"])} questions')
"

# Run OCR batch (if more PDFs need processing)
python3 scripts/batch_ocr_pipeline.py --dry-run    # preview
python3 scripts/batch_ocr_pipeline.py --max-pdfs 5  # process 5

# Inject new OCR output into database
python3 scripts/inject_from_ocr.py --dry-run        # preview
python3 scripts/inject_from_ocr.py                  # actual injection

# === PRODUCTION DEPLOY ===
# Set env vars in Netlify dashboard:
#   Site settings > Environment variables
#   SUPABASE_URL = https://xxxxxxxxxxxx.supabase.co
#   SUPABASE_ANON_KEY = eyJhbGciOi...
# Deploy
git add -A
git commit -m "Descriptive message"
git push   # Netlify auto-deploys from main
```

---

*End of handoff document. If you're a new AI agent: read this entire file, then explore any area you need to modify. The codebase is deliberately simple — pure HTML/CSS/JS with static JSON data. Don't over-engineer it.*
