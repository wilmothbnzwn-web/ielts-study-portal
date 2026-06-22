-- ================================================================
-- IELTS Study Portal — Supabase Database Migration
-- Run this SQL in your Supabase project's SQL Editor:
--   https://app.supabase.com/project/<your-project>/sql/new
-- ================================================================

-- 1. Create tables
CREATE TABLE IF NOT EXISTS public.user_words (
  id               UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id          UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  word             TEXT NOT NULL,
  chinese          TEXT NOT NULL DEFAULT '',
  phonetic         TEXT NOT NULL DEFAULT '',
  audio_url        TEXT NOT NULL DEFAULT '',
  synonyms         TEXT NOT NULL DEFAULT '',
  context_sentence TEXT NOT NULL DEFAULT '',
  saved_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.user_sentences (
  id               UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id          UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  sentence         TEXT NOT NULL,
  chinese          TEXT NOT NULL DEFAULT '',
  high_freq_words  TEXT NOT NULL DEFAULT '',
  saved_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2. Create indexes for fast per-user queries
CREATE INDEX IF NOT EXISTS idx_user_words_user_id ON public.user_words(user_id);
CREATE INDEX IF NOT EXISTS idx_user_words_saved_at ON public.user_words(user_id, saved_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_sentences_user_id ON public.user_sentences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sentences_saved_at ON public.user_sentences(user_id, saved_at DESC);

-- 3. Enable Row-Level Security
ALTER TABLE public.user_words ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_sentences ENABLE ROW LEVEL SECURITY;

-- 4. RLS Policies: users can only access their own data

-- SELECT
CREATE POLICY "Users can view own words"
  ON public.user_words FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can view own sentences"
  ON public.user_sentences FOR SELECT
  USING (auth.uid() = user_id);

-- INSERT (client must set user_id = auth.uid(); RLS enforces this)
CREATE POLICY "Users can insert own words"
  ON public.user_words FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can insert own sentences"
  ON public.user_sentences FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- DELETE
CREATE POLICY "Users can delete own words"
  ON public.user_words FOR DELETE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own sentences"
  ON public.user_sentences FOR DELETE
  USING (auth.uid() = user_id);

-- UPDATE (for future use)
CREATE POLICY "Users can update own words"
  ON public.user_words FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own sentences"
  ON public.user_sentences FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- 5. (Optional) Disable email confirmation for development:
-- Go to: Authentication > Settings > Auth Settings
-- Toggle "Confirm email" to OFF for local testing
-- IMPORTANT: Turn this back ON for production!
