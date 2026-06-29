-- ================================================================
-- IELTS Study Portal — Supabase Migration
-- Migration: Create wrong_questions (mistake book / 错题本) table
-- Timestamp: 20250629120000
-- ================================================================

-- 1. Create wrong_questions table
CREATE TABLE IF NOT EXISTS public.wrong_questions (
  id               UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id          UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  question_id      TEXT NOT NULL,
  question_type    TEXT NOT NULL DEFAULT 'reading',  -- 'reading' | 'vocabulary'
  question_payload JSONB DEFAULT '{}'::jsonb,        -- cached question metadata
  source_type      TEXT NOT NULL DEFAULT 'manual',   -- 'manual' | 'exam' | 'practice'
  source_exam_id   TEXT,                              -- test id or deck id
  wrong_count      INTEGER NOT NULL DEFAULT 1,
  first_added_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_wrong_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  -- Prevent duplicate entries: one record per user per question per type
  UNIQUE(user_id, question_id, question_type)
);

-- 2. Indexes for fast per-user queries and filtering
CREATE INDEX IF NOT EXISTS idx_wq_user_id        ON public.wrong_questions(user_id);
CREATE INDEX IF NOT EXISTS idx_wq_last_wrong     ON public.wrong_questions(user_id, last_wrong_at DESC);
CREATE INDEX IF NOT EXISTS idx_wq_question_type   ON public.wrong_questions(user_id, question_type);
CREATE INDEX IF NOT EXISTS idx_wq_source_type     ON public.wrong_questions(user_id, source_type);

-- 3. Enable Row-Level Security
ALTER TABLE public.wrong_questions ENABLE ROW LEVEL SECURITY;

-- 4. RLS Policies: users can only access their own data

-- SELECT
CREATE POLICY "Users can view own wrong questions"
  ON public.wrong_questions FOR SELECT
  USING (auth.uid() = user_id);

-- INSERT (client must set user_id = auth.uid(); RLS enforces this)
CREATE POLICY "Users can insert own wrong questions"
  ON public.wrong_questions FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- UPDATE
CREATE POLICY "Users can update own wrong questions"
  ON public.wrong_questions FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- DELETE
CREATE POLICY "Users can delete own wrong questions"
  ON public.wrong_questions FOR DELETE
  USING (auth.uid() = user_id);
