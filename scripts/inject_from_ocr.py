#!/usr/bin/env python3
"""
Auto-Structure Injector: Parse OCR output → structured reading test JSON.
Reads each PDF's OCR output, detects passages + questions, builds test objects,
and appends them to reading_tests.json.

Usage: python3 inject_from_ocr.py [--dry-run] [--max-tests N]
"""
import json
import os
import re
import sys
import html
import argparse
from pathlib import Path
from collections import OrderedDict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OCR_OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'scripts', 'ocr_output')
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'reading_tests.json')

# Sources already injected (skip these OCR outputs)
SKIP_SOURCES = {'阅读17', 'predict17'}

MIN_WORD_COUNT = 500  # Minimum words for a valid passage
MIN_QUESTIONS = 6      # Minimum questions per passage
MAX_TESTS_PER_PDF = 4  # Max passages to extract per PDF (typical IELTS prediction book has 3-4)

TOPIC_KEYWORDS = {
    'Science': ['science', 'scientific', 'mri', 'brain', 'neuron', 'neuroscience', 'psychology',
                'cognitive', 'genetic', 'dna', 'species', 'biology', 'chemical', 'fossil',
                'mammal', 'primate', 'experiment', 'laboratory', 'quantum', 'physics',
                'fMRI', 'scanning', 'cortex'],
    'Technology': ['technology', 'internet', 'computer', 'digital', 'software', 'robot',
                   'artificial', 'automation', 'electronic', 'wireless', 'device', 'machine',
                   'innovation', 'invention', 'driverless', 'vehicle'],
    'Environment': ['environment', 'climate', 'pollution', 'carbon', 'sustainable', 'ecological',
                    'biodiversity', 'conservation', 'sea', 'ocean', 'aral', 'water', 'river',
                    'forest', 'species', 'wildlife', 'desert', 'salinity', 'irrigation'],
    'History': ['history', 'ancient', 'century', 'archaeology', 'civilization', 'empire',
                'medieval', 'roman', 'egypt', 'trade route', 'silk', 'industrial'],
    'Economics': ['economic', 'economy', 'market', 'trade', 'business', 'corporate', 'company',
                  'commercial', 'profit', 'price', 'capital', 'investment', 'stock', 'labor',
                  'employee', 'consumer', 'money', 'financial'],
    'Sociology': ['social', 'society', 'education', 'culture', 'language', 'community',
                  'migration', 'urban', 'population', 'health', 'disease', 'medical',
                  'lie detection', 'ethical', 'ethics', 'behavior', 'interaction'],
}


def detect_topic(text):
    """Detect topic from passage text by keyword matching."""
    text_lower = text.lower()
    scores = {}
    for topic, keywords in TOPIC_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text_lower)
        if score > 0:
            scores[topic] = score
    if scores:
        return max(scores, key=scores.get)
    return 'Science'  # Default


def detect_difficulty(text):
    """Estimate difficulty (1-5) based on text complexity heuristics."""
    words = text.split()
    if len(words) < 300:
        return 2
    # Average word length heuristic
    avg_word_len = sum(len(w) for w in words) / max(len(words), 1)
    # Sentence length heuristic
    sentences = re.split(r'[.!?]+', text)
    avg_sent_len = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)

    if avg_word_len > 5.5 and avg_sent_len > 22:
        return 4
    elif avg_word_len > 5.0 and avg_sent_len > 18:
        return 3
    elif avg_word_len > 4.5:
        return 3
    return 2


def extract_title(text, source_label):
    """Extract a title from the first meaningful lines of the passage."""
    # Strip HTML tags first
    clean_text = re.sub(r'<[^>]+>', '', text)
    lines = [l.strip() for l in clean_text.split('\n') if l.strip() and len(l.strip()) > 15]

    # Skip garbled OCR lines (too many special chars)
    clean_lines = []
    for l in lines:
        alpha_ratio = sum(1 for c in l if c.isalpha() or c.isspace()) / max(len(l), 1)
        if alpha_ratio > 0.65:
            clean_lines.append(l)

    if clean_lines:
        # First meaningful line that looks like a title (not starting lowercase, not a paragraph)
        for line in clean_lines[:5]:
            cleaned = re.sub(r'[\[\]\(\){}|#@*]', '', line).strip()
            cleaned = re.sub(r'\s+', ' ', cleaned)
            if len(cleaned) > 15 and cleaned[0].isupper():
                # Truncate to reasonable title length
                words = cleaned.split()
                if len(words) > 12:
                    cleaned = ' '.join(words[:12]) + '...'
                return cleaned

    # Fallback: use first clean line
    if clean_lines:
        cleaned = re.sub(r'[\[\]\(\){}|#@*]', '', clean_lines[0]).strip()
        cleaned = re.sub(r'\s+', ' ', cleaned)
        words = cleaned.split()
        if len(words) > 12:
            cleaned = ' '.join(words[:12]) + '...'
        return cleaned

    return f"IELTS Reading — {source_label}"


# ── OCR Text Parser ────────────────────────────────────
def parse_ocr_text(raw_text, source_label):
    """Parse OCR raw text into list of {passage_text, questions, metadata} dicts."""
    # Clean up OCR artifacts
    lines = raw_text.split('\n')

    # Find passage boundaries by detecting lettered paragraph starts
    # Pattern: a line starting with a capital letter followed by space/newline
    # This matches IELTS passage paragraph labeling (A, B, C, D...)

    passages = []
    current_passage_lines = []
    current_questions = []
    in_questions = False
    question_buffer = []
    passage_count = 0

    # State machine for parsing
    STATE_IDLE = 'idle'
    STATE_PASSAGE = 'passage'
    STATE_QUESTIONS = 'questions'
    state = STATE_IDLE

    # Track paragraph letters seen
    para_letters_seen = set()
    last_was_para_header = False

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines and pure noise
        if not line:
            i += 1
            continue

        # Detect paragraph letter header (A, B, C, D, E, F, G, H, I, J)
        para_match = re.match(r'^([A-I])\s{1,5}(\S.*)$', line)
        # Also match letter-only on its own line (sometimes OCR splits them)
        solo_letter_match = re.match(r'^([A-I])$', line)

        # Detect question section start
        q_section_match = re.match(r'.*Questions?\s+(\d+)\s*[-–—]\s*(\d+).*', line, re.IGNORECASE)

        # Detect TRUE/FALSE/NOT GIVEN instruction
        is_tfn = bool(re.search(r'TRUE.*FALSE.*NOT GIVEN', line, re.IGNORECASE))

        if para_match and state != STATE_QUESTIONS:
            # Started a new lettered paragraph → we're in a passage
            if state == STATE_IDLE:
                state = STATE_PASSAGE
            letter = para_match.group(1)
            para_letters_seen.add(letter)
            current_passage_lines.append(line)
            last_was_para_header = True

        elif solo_letter_match and state != STATE_QUESTIONS:
            # Letter on its own line (OCR artifact)
            letter = solo_letter_match.group(1)
            # Check if next line looks like paragraph text
            if i + 1 < len(lines) and len(lines[i+1].strip()) > 30:
                if state == STATE_IDLE:
                    state = STATE_PASSAGE
                para_letters_seen.add(letter)
                current_passage_lines.append(line)
                last_was_para_header = True

        elif q_section_match and state == STATE_PASSAGE:
            # Transition: passage text → questions
            # Save current passage
            if len(current_passage_lines) > 10 and len(para_letters_seen) >= 3:
                passage_text = clean_passage_text('\n'.join(current_passage_lines))
                wc = estimate_word_count(passage_text)
                if wc >= 400:  # Real IELTS passages are 700-1000+ words
                    passage_count += 1
                    passages.append({
                        'text': passage_text,
                        'para_count': len(para_letters_seen),
                        'questions_start_line': i,
                        'word_count': wc,
                    })

            # Reset and start questions
            state = STATE_QUESTIONS
            in_questions = True
            question_buffer = [line]
            current_passage_lines = []
            para_letters_seen = set()

        elif state == STATE_QUESTIONS:
            # Check if we're transitioning to a new passage (next lettered paragraph appears)
            next_para = re.match(r'^([A-I])\s{1,5}(\S.*)$', line)
            if next_para and len(question_buffer) > 0:
                # End of questions, start of new passage
                current_questions = extract_questions('\n'.join(question_buffer))
                if passages:
                    passages[-1]['questions'] = current_questions
                question_buffer = []
                state = STATE_PASSAGE
                current_passage_lines.append(line)
                para_letters_seen.add(next_para.group(1))
            else:
                question_buffer.append(line)

        elif state == STATE_PASSAGE:
            current_passage_lines.append(line)

        i += 1

    # Don't forget the last passage
    if state == STATE_PASSAGE and len(current_passage_lines) > 10 and len(para_letters_seen) >= 3:
        passage_text = clean_passage_text('\n'.join(current_passage_lines))
        if estimate_word_count(passage_text) >= 400:
            passage_count += 1
            passages.append({
                'text': passage_text,
                'para_count': len(para_letters_seen),
                'questions_start_line': -1,
            })

    # Handle last question set
    if question_buffer:
        current_questions = extract_questions('\n'.join(question_buffer))
        if passages:
            passages[-1]['questions'] = current_questions

    return passages


def clean_passage_text(text):
    """Clean OCR passage text and convert to HTML paragraphs."""
    lines = text.split('\n')
    paragraphs = []
    current_para = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_para:
                para_text = ' '.join(current_para)
                # Clean OCR artifacts
                para_text = re.sub(r'\s+', ' ', para_text)
                para_text = re.sub(r'\[\s*[ée]\s*', '', para_text)  # Remove [é artifacts
                para_text = re.sub(r'4hoe\b', '', para_text)
                para_text = re.sub(r'redicting\b', '', para_text)
                if len(para_text) > 20:
                    paragraphs.append(para_text)
                current_para = []
            continue

        # Remove Chinese watermarks and garbled lines
        chinese_ratio = sum(1 for c in stripped if '一' <= c <= '鿿') / max(len(stripped), 1)
        if chinese_ratio > 0.5:
            # Skip heavy Chinese lines (watermarks/ads)
            continue

        # Remove lines that are mostly special chars (OCR noise)
        alpha_ratio = sum(1 for c in stripped if c.isalpha() or c.isspace() or c in '.,;:!?-\'"()') / max(len(stripped), 1)
        if alpha_ratio < 0.5 and len(stripped) > 10:
            continue

        # Remove paragraph letter markers at start
        stripped = re.sub(r'^[A-I]\s{1,5}', '', stripped)

        current_para.append(stripped)

    # Don't forget last paragraph
    if current_para:
        para_text = ' '.join(current_para)
        para_text = re.sub(r'\s+', ' ', para_text)
        if len(para_text) > 20:
            paragraphs.append(para_text)

    # Convert to HTML
    html_paras = [f'<p>{html.escape(p)}</p>' for p in paragraphs if len(p) > 20]
    return '\n'.join(html_paras)


def extract_questions(q_text):
    """Extract question objects from question section text."""
    questions = []
    lines = q_text.split('\n')

    # Detect question type
    is_tfn = bool(re.search(r'TRUE.*FALSE.*NOT GIVEN|Do the following statements agree', q_text, re.IGNORECASE))
    is_short_answer = bool(re.search(r'No\s*More than\s*(Three|Two|One|3|2|1)\s*words', q_text, re.IGNORECASE))
    is_summary = bool(re.search(r'Complete the following summary|Complete the summary', q_text, re.IGNORECASE))
    is_matching = bool(re.search(r'match the people|Match each|Choose the correct letter', q_text, re.IGNORECASE))
    is_multiple_choice = bool(re.search(r'Choose the correct letter.*[ABCD]', q_text, re.IGNORECASE))

    # Extract word limit for summary/short answer
    word_limit = None
    wl_match = re.search(r'No\s*More than\s*(Three|Two|One|\d+)\s*words?', q_text, re.IGNORECASE)
    if wl_match:
        wl_map = {'one': 1, 'two': 2, 'three': 3, '1': 1, '2': 2, '3': 3}
        wl_str = wl_match.group(1).lower()
        word_limit = wl_map.get(wl_str, 3)

    # Parse individual questions
    q_num = 1
    for line in lines:
        stripped = line.strip()
        # Skip garbled/noise lines
        if len(stripped) < 10:
            continue
        alpha_ratio = sum(1 for c in stripped if c.isalpha() or c.isspace() or c in '.,;:!?-\'"()') / max(len(stripped), 1)
        if alpha_ratio < 0.5:
            continue

        # Question number pattern: "1 " or "1." or "1-" at start
        q_match = re.match(r'^(\d{1,2})\s*[\.\)\-]\s*(.+)', stripped)
        if q_match:
            num = int(q_match.group(1))
            q_body = q_match.group(2).strip()

            # Skip instruction lines masquerading as questions
            if len(q_body) < 5:
                continue
            if q_body.lower().startswith(('write ', 'complete ', 'choose ', 'in boxes', 'NB ', 'do the', 'true', 'false')):
                continue

            q_obj = {
                'id': len(questions) + 1,
                'questionText': q_body,
            }

            if is_tfn:
                q_obj['type'] = 'true_false_not_given'
                q_obj['options'] = ['TRUE', 'FALSE', 'NOT GIVEN']
                q_obj['correctAnswer'] = 0  # Placeholder
            elif is_short_answer or is_summary:
                q_obj['type'] = 'short_answer'
                q_obj['correctAnswer'] = '(see answer key)'
                if word_limit:
                    q_obj['wordLimit'] = word_limit
            elif is_multiple_choice:
                q_obj['type'] = 'short_answer'
                q_obj['correctAnswer'] = '(see answer key)'
            elif is_matching:
                q_obj['type'] = 'short_answer'
                q_obj['correctAnswer'] = '(see answer key)'
            else:
                # Default to short answer for unrecognized types
                q_obj['type'] = 'short_answer'
                q_obj['correctAnswer'] = '(see answer key)'

            if len(q_body) > 10:
                questions.append(q_obj)
            q_num += 1

    return questions


def estimate_word_count(html_text):
    """Estimate word count from HTML passage text."""
    clean = re.sub(r'<[^>]+>', ' ', html_text)
    return len(clean.split())


def build_test_object(passage_idx, passage_data, source_pdf, pdf_label):
    """Build a reading_tests.json test object from parsed passage data."""
    title = extract_title(passage_data['text'], pdf_label)
    topic = detect_topic(passage_data['text'])
    difficulty = detect_difficulty(passage_data['text'])
    word_count = estimate_word_count(passage_data['text'])
    questions = passage_data.get('questions', [])

    # Generate unique ID
    safe_label = re.sub(r'[^a-zA-Z0-9]', '-', pdf_label).lower()
    safe_label = re.sub(r'-+', '-', safe_label).strip('-')
    test_id = f'{safe_label}-p{passage_idx}'

    # Ensure minimum viable questions
    if not questions:
        # Generate placeholder questions from passage text
        questions = generate_placeholder_questions(passage_data['text'])

    question_count = len(questions)
    total_time = max(1200, word_count * 4)  # ~4 seconds per word

    return {
        'id': test_id,
        'title': title,
        'topic': topic,
        'source': f'IELTS Reading Prediction — {pdf_label} Passage {passage_idx}',
        'difficulty': difficulty,
        'totalTime': total_time,
        'wordCount': word_count,
        'questionCount': question_count,
        'passageText': passage_data['text'],
        'questions': questions,
    }


def generate_placeholder_questions(passage_html):
    """Generate basic TFN questions when parsing fails to find question sections."""
    # Clean HTML to get plain text
    clean = re.sub(r'<[^>]+>', '', passage_html)
    sentences = re.split(r'(?<=[.!?])\s+', clean)
    # Pick meaningful sentences
    candidates = [s.strip() for s in sentences if 30 < len(s.strip()) < 200]

    questions = []
    for i, sentence in enumerate(candidates[:8]):
        # Create a simple TFN question by slightly modifying a sentence
        q_text = sentence[:150].rstrip('.,;:!?') + '.'
        questions.append({
            'id': i + 1,
            'type': 'true_false_not_given',
            'questionText': q_text,
            'options': ['TRUE', 'FALSE', 'NOT GIVEN'],
            'correctAnswer': 0,  # Default to TRUE
        })

    return questions


# ── Main ────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Parse but do not modify reading_tests.json')
    parser.add_argument('--max-tests', type=int, default=0, help='Max tests to inject (0=all)')
    parser.add_argument('--max-pdfs', type=int, default=0, help='Max PDFs to process (0=all)')
    parser.add_argument('--min-chars', type=int, default=5000, help='Min chars in OCR output to process')
    args = parser.parse_args()

    print('='*60)
    print('📝 OCR → Test JSON Auto-Structuring Injector')
    print('='*60)

    # Find all OCR output files
    ocr_files = sorted(Path(OCR_OUTPUT_DIR).glob('*.txt'))
    # Filter out batch summary
    ocr_files = [f for f in ocr_files if not f.name.startswith('_')]

    if not ocr_files:
        # Also check .json files
        ocr_files = sorted(Path(OCR_OUTPUT_DIR).glob('*.json'))
        ocr_files = [f for f in ocr_files if not f.name.startswith('_')]
        if not ocr_files:
            print('❌ No OCR output files found in', OCR_OUTPUT_DIR)
            print('   Run batch_ocr_pipeline.py first!')
            return

    print(f'\n📁 Found {len(ocr_files)} OCR output files')

    # Load existing database
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)

    existing_ids = {t['id'] for t in db['tests']}
    print(f'📊 Existing: {len(db["tests"])} tests, {sum(t["questionCount"] for t in db["tests"])} questions')

    # Process each OCR output
    new_tests = []
    skipped = 0
    errors = 0
    pdfs_processed = 0

    for ocr_file in ocr_files:
        if args.max_pdfs > 0 and pdfs_processed >= args.max_pdfs:
            break

        label = ocr_file.stem[:50]

        # Skip already-processed sources
        should_skip = False
        for skip_src in SKIP_SOURCES:
            if skip_src in label:
                print(f'\n{"─"*50}')
                print(f'📄 SKIP: {label} (already processed)')
                should_skip = True
                break
        if should_skip:
            skipped += 1
            continue

        print(f'\n{"─"*50}')
        print(f'📄 Processing: {label}')

        # Load OCR text
        if ocr_file.suffix == '.json':
            with open(ocr_file, 'r', encoding='utf-8') as f:
                page_data = json.load(f)
            raw_text = '\n'.join(p.get('text', '') for p in page_data)
        else:
            with open(ocr_file, 'r', encoding='utf-8') as f:
                raw_text = f.read()

        if len(raw_text) < args.min_chars:
            print(f'  ⏭  SKIP: Too little text ({len(raw_text)} chars)')
            skipped += 1
            continue

        # Parse passages
        try:
            passages = parse_ocr_text(raw_text, label)
        except Exception as e:
            print(f'  ❌ Parse error: {e}')
            errors += 1
            continue

        if not passages:
            print(f'  ⚠️  No passages detected')
            skipped += 1
            continue

        print(f'  📖 Found {len(passages)} passage(s)')

        # Quality filter: sort by word count, take top N per PDF
        passages_sorted = sorted(
            passages,
            key=lambda p: (p.get('word_count', 0), len(p.get('text', ''))),
            reverse=True
        )

        pdf_test_count = 0
        for p_idx, p_data in enumerate(passages_sorted, 1):
            if args.max_tests > 0 and len(new_tests) >= args.max_tests:
                break
            if pdf_test_count >= MAX_TESTS_PER_PDF:
                break

            wc = p_data.get('word_count', 0)
            qc = len(p_data.get('questions', []))

            # Quality filters
            if wc < MIN_WORD_COUNT:
                continue
            if qc < MIN_QUESTIONS:
                # Supplement with placeholder questions if passage text is good
                if wc >= 600:
                    p_data['questions'] = generate_placeholder_questions(p_data['text'])
                else:
                    continue

            # Title quality check: skip passages whose title is mostly OCR noise
            raw_title = extract_title(p_data['text'], label)
            alpha_ratio = sum(1 for c in raw_title if c.isascii() and c.isalpha() or c.isspace()) / max(len(raw_title), 1)
            if alpha_ratio < 0.55:
                continue

            try:
                test_obj = build_test_object(p_idx, p_data, ocr_file.name, label)
                tid = test_obj['id']

                if tid in existing_ids:
                    print(f'    ⚠️  {tid}: already exists, skipping')
                    continue

                new_tests.append(test_obj)
                existing_ids.add(tid)
                pdf_test_count += 1
                print(f'    ✅ {tid}: "{test_obj["title"][:50]}..." | {test_obj["topic"]} | {test_obj["questionCount"]}q | {test_obj["wordCount"]}w')

            except Exception as e:
                print(f'    ❌ Error building test {p_idx}: {e}')
                errors += 1

        pdfs_processed += 1

    # ── Inject into database ──
    print(f'\n{"="*60}')
    print(f'📊 INJECTION SUMMARY')
    print(f'{"="*60}')
    print(f'  ✅ New tests:     {len(new_tests)}')
    print(f'  ⏭  Skipped PDFs:  {skipped}')
    print(f'  ❌ Errors:        {errors}')
    print(f'  📊 Existing:      {len(db["tests"])}')
    print(f'  📊 After inject:  {len(db["tests"]) + len(new_tests)}')

    if not new_tests:
        print('\n⚠️  No new tests to inject.')
        return

    if args.dry_run:
        print('\n🔍 DRY RUN — no changes made.')
        print('\nNew tests preview:')
        for t in new_tests:
            print(f'  {t["id"]}: {t["title"][:60]} | {t["topic"]} | {t["questionCount"]}q')
        return

    # Append new tests
    db['tests'].extend(new_tests)

    # Validate JSON
    json_str = json.dumps(db, ensure_ascii=False, indent=2)
    try:
        json.loads(json_str)  # Verify round-trip
    except json.JSONDecodeError as e:
        print(f'❌ JSON validation failed: {e}')
        return

    # Backup
    backup_path = DB_PATH + f'.backup.{int(__import__("time").time())}'
    import shutil
    shutil.copy2(DB_PATH, backup_path)
    print(f'💾 Backup: {backup_path}')

    # Write
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        f.write(json_str)

    total_tests = len(db['tests'])
    total_questions = sum(t['questionCount'] for t in db['tests'])
    print(f'\n✅ SUCCESS: Injected {len(new_tests)} new tests')
    print(f'📊 Final: {total_tests} tests, {total_questions} questions')
    print(f'💾 Written to: {DB_PATH}')


if __name__ == '__main__':
    main()
