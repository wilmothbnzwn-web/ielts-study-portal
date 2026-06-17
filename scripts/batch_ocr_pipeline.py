#!/usr/bin/env python3
"""
Batch OCR Pipeline: Process ALL remaining IELTS reading prediction PDFs.
Phase 1: OCR extraction with smart page selection
Phase 2: Auto-detect passages and questions from OCR text
Phase 3: Append to reading_tests.json

Usage: python3 batch_ocr_pipeline.py [--dry-run] [--max-pdfs N] [--dpi 200]
"""
import json
import os
import re
import sys
import time
import argparse
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract

# ── Config ──────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OCR_OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'scripts', 'ocr_output')
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'reading_tests.json')
PDF_LIBRARY = '/Users/zzzzhangjintao/Desktop/IELTS_Organized_Library/02_阅读专项精读库_Reading_by_Topic/07_Reading_Methodology_and_Skills/我预测阅读机经库'

DPI = 200  # Balance quality vs speed (lower = faster, still readable)
LANG = 'eng+chi_sim'
SKIP_PDFS = {'阅读17.pdf'}  # Already processed

# Page range: skip covers (p1-5), read content pages (p6-60), skip appendix
PAGE_START = 6
PAGE_MAX = 65  # Max pages to OCR per PDF

os.makedirs(OCR_OUTPUT_DIR, exist_ok=True)


# ── Priority scoring ────────────────────────────────────
def priority_score(filename):
    """Higher score = process first. 新版+全文 > 新版 > 全文 > rest"""
    score = 0
    if '新版' in filename:
        score += 10
    if '全文' in filename:
        score += 8
    if '新' in filename.replace('新版', ''):
        score += 3
    if '修订' in filename:
        score += 2
    if '改' in filename:
        score += 2
    # Higher number = newer edition (rough heuristic)
    num_match = re.search(r'阅读(\d+)', filename)
    if num_match:
        score += int(num_match.group(1)) * 0.01
    return score


def scan_pdfs(library_path):
    """Scan library, return sorted list of PDFs to process."""
    pdfs = []
    lib = Path(library_path)

    for pdf_path in sorted(lib.rglob('*.pdf')):
        fname = pdf_path.name
        if fname in SKIP_PDFS:
            print(f'  SKIP (already done): {fname}')
            continue

        # Skip if OCR output already exists
        safe = re.sub(r'[^a-zA-Z0-9一-鿿_-]', '_', fname)
        existing_txt = os.path.join(OCR_OUTPUT_DIR, f'{safe}.txt')
        if os.path.exists(existing_txt) and os.path.getsize(existing_txt) > 10000:
            # Already processed, check quality
            print(f'  SKIP (already OCR\'d): {fname} ({os.path.getsize(existing_txt)//1024}KB)')
            continue

        # Skip duplicates (阅读33 has both 新版 and non-新版)
        # We prefer 新版 versions
        pdfs.append({
            'path': str(pdf_path),
            'name': fname,
            'size_mb': pdf_path.stat().st_size / (1024 * 1024),
            'priority': priority_score(fname),
        })

    # Sort by priority descending
    pdfs.sort(key=lambda x: (-x['priority'], x['name']))
    return pdfs


# ── OCR Engine ──────────────────────────────────────────
def ocr_pdf(pdf_path, label, dpi=DPI, page_start=PAGE_START, page_max=PAGE_MAX):
    """OCR a PDF, returning list of {page, text, chars, english_ratio} dicts."""
    print(f'\n{"="*60}')
    print(f'🔍 OCR: {label}')
    print(f'   File: {pdf_path}')
    t0 = time.time()

    try:
        images = convert_from_path(pdf_path, dpi=dpi, first_page=page_start,
                                    last_page=min(page_start + page_max, 200))
        total = len(images)
        print(f'   Pages: {total} (starting at page {page_start}) @ {dpi} DPI')
    except Exception as e:
        print(f'   ❌ ERROR converting PDF: {e}')
        return [], str(e)

    results = []
    errors = []
    for idx, img in enumerate(images):
        real_page = page_start + idx
        try:
            text = pytesseract.image_to_string(img, lang=LANG).strip()

            if not text or len(text) < 50:
                continue  # Skip near-empty pages

            # Calculate English character ratio
            eng_chars = sum(1 for c in text if c.isascii() and c.isalpha())
            total_chars = sum(1 for c in text if c.isalpha())
            eng_ratio = eng_chars / max(total_chars, 1)

            results.append({
                'page': real_page,
                'text': text,
                'chars': len(text),
                'eng_ratio': round(eng_ratio, 2),
            })

        except Exception as e:
            errors.append(f'Page {real_page}: {e}')
            continue

    elapsed = time.time() - t0
    content_pages = [r for r in results if r['chars'] > 200 and r['eng_ratio'] > 0.4]
    print(f'   ✅ {len(results)} pages with text ({len(content_pages)} content-rich)')
    print(f'   ⏱  {elapsed:.1f}s')
    if errors:
        print(f'   ⚠️  {len(errors)} page errors')
        for e in errors[:3]:
            print(f'      {e}')

    return results, None


def save_raw_text(label, results):
    """Save raw OCR output to .txt and .json files."""
    safe = re.sub(r'[^a-zA-Z0-9一-鿿_-]', '_', label)
    txt_path = os.path.join(OCR_OUTPUT_DIR, f'{safe}.txt')
    json_path = os.path.join(OCR_OUTPUT_DIR, f'{safe}.json')

    with open(txt_path, 'w', encoding='utf-8') as f:
        for r in results:
            f.write(f"\n{'='*60}\n")
            f.write(f"=== PAGE {r['page']} ({r['chars']} chars, {r['eng_ratio']} eng) ===\n")
            f.write(f"{'='*60}\n")
            f.write(r['text'])
            f.write('\n')

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    total_chars = sum(r['chars'] for r in results)
    print(f'   💾 Saved: {txt_path} ({total_chars} chars)')
    return txt_path, json_path


# ── Content Analysis ────────────────────────────────────
def analyze_content(results):
    """Analyze OCR results to determine if content is usable for test extraction."""
    if not results:
        return {'usable': False, 'reason': 'No text extracted'}

    content_pages = [r for r in results if r['chars'] > 200 and r['eng_ratio'] > 0.4]
    total_chars = sum(r['chars'] for r in results)
    avg_eng = sum(r['eng_ratio'] for r in results) / len(results) if results else 0

    # Check for passage markers
    full_text = '\n'.join(r['text'] for r in results)
    has_questions = bool(re.search(r'(?:Questions?\s+\d+|TRUE|FALSE|NOT GIVEN|YES|NO)', full_text, re.IGNORECASE))
    has_passages = bool(re.search(r'(?:Reading Passage|PASSAGE|passage\s+\d)', full_text))
    has_chinese_markers = bool(re.search(r'(?:第[一二三四五六七八九十\d]+篇|阅读文章|阅读理解)', full_text))

    return {
        'usable': len(content_pages) >= 8 and avg_eng > 0.5,
        'content_pages': len(content_pages),
        'total_chars': total_chars,
        'avg_eng_ratio': round(avg_eng, 2),
        'has_questions': has_questions,
        'has_passages': has_passages,
        'has_chinese_markers': has_chinese_markers,
        'confidence': 'high' if (len(content_pages) >= 15 and avg_eng > 0.6 and has_questions)
                      else 'medium' if (len(content_pages) >= 8 and avg_eng > 0.5)
                      else 'low',
    }


# ── Main Batch Runner ───────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Only list PDFs, no OCR')
    parser.add_argument('--max-pdfs', type=int, default=0, help='Limit number of PDFs to process (0=all)')
    parser.add_argument('--dpi', type=int, default=DPI, help=f'OCR DPI (default {DPI})')
    parser.add_argument('--start-page', type=int, default=PAGE_START, help=f'Start page (default {PAGE_START})')
    parser.add_argument('--max-pages', type=int, default=PAGE_MAX, help=f'Max pages per PDF (default {PAGE_MAX})')
    args = parser.parse_args()

    print('='*60)
    print('📚 IELTS Reading Prediction PDF — Batch OCR Pipeline')
    print('='*60)

    # Scan
    pdfs = scan_pdfs(PDF_LIBRARY)
    print(f'\n📋 Found {len(pdfs)} PDFs to process:\n')

    for i, p in enumerate(pdfs):
        tag = ''
        if '新版' in p['name']:
            tag += '🆕新版 '
        if '全文' in p['name']:
            tag += '📄全文 '
        if not tag:
            tag = '📘'
        print(f'  {i+1:2d}. [{p["priority"]:5.1f}] {tag} {p["name"]} ({p["size_mb"]:.0f}MB)')

    if args.dry_run:
        print('\n✅ Dry run complete. Use without --dry-run to process.')
        return

    if args.max_pdfs > 0:
        pdfs = pdfs[:args.max_pdfs]
        print(f'\n⚠️  Limited to first {args.max_pdfs} PDFs')

    # Process
    summary = []
    for i, pdf_info in enumerate(pdfs):
        print(f'\n{"#"*60}')
        print(f'# [{i+1}/{len(pdfs)}] {pdf_info["name"]}')
        print(f'{"#"*60}')

        results, error = ocr_pdf(
            pdf_info['path'],
            pdf_info['name'],
            dpi=args.dpi,
            page_start=args.start_page,
            page_max=args.max_pages,
        )

        if error:
            summary.append({
                'name': pdf_info['name'],
                'status': 'ERROR',
                'error': error,
                'pages': 0,
                'total_chars': 0,
                'analysis': {'usable': False, 'reason': error},
            })
            print(f'   ❌ SKIPPED due to error: {error}')
            continue

        if not results:
            summary.append({
                'name': pdf_info['name'],
                'status': 'EMPTY',
                'error': None,
                'pages': 0,
                'total_chars': 0,
                'analysis': {'usable': False, 'reason': 'No text extracted'},
            })
            print(f'   ⚠️  SKIPPED: No text extracted')
            continue

        # Save raw output
        txt_path, json_path = save_raw_text(pdf_info['name'], results)

        # Analyze
        analysis = analyze_content(results)
        status = 'OK' if analysis['usable'] else 'LOW_QUALITY'
        summary.append({
            'name': pdf_info['name'],
            'status': status,
            'error': None,
            'pages': len(results),
            'total_chars': analysis['total_chars'],
            'txt_path': txt_path,
            'json_path': json_path,
            'analysis': analysis,
        })

        print(f'   📊 Analysis: {analysis["confidence"]} confidence, '
              f'{analysis["content_pages"]} content pages, '
              f'{analysis["avg_eng_ratio"]:.0%} avg eng, '
              f'Q:{"Y" if analysis["has_questions"] else "N"} '
              f'P:{"Y" if analysis["has_passages"] else "N"}')

    # Final summary
    print(f'\n{"="*60}')
    print(f'📊 BATCH SUMMARY')
    print(f'{"="*60}')
    ok = [s for s in summary if s['status'] == 'OK']
    low = [s for s in summary if s['status'] == 'LOW_QUALITY']
    err = [s for s in summary if s['status'] in ('ERROR', 'EMPTY')]

    print(f'  ✅ High quality:  {len(ok)} PDFs')
    print(f'  ⚠️  Low quality:  {len(low)} PDFs')
    print(f'  ❌ Errors/Empty: {len(err)} PDFs')
    print(f'  📝 Total chars:  {sum(s["total_chars"] for s in summary):,}')

    if ok:
        print(f'\n  High quality PDFs:')
        for s in ok:
            a = s['analysis']
            print(f'    ✅ {s["name"]} — {a["content_pages"]} pages, {a["avg_eng_ratio"]:.0%} eng, confidence={a["confidence"]}')

    if low:
        print(f'\n  Low quality PDFs (may need manual review):')
        for s in low:
            a = s['analysis']
            print(f'    ⚠️  {s["name"]} — {a["content_pages"]} pages, {a["avg_eng_ratio"]:.0%} eng')

    if err:
        print(f'\n  Errors:')
        for s in err:
            print(f'    ❌ {s["name"]} — {s.get("error", s["analysis"].get("reason", "unknown"))}')

    # Save summary
    summary_path = os.path.join(OCR_OUTPUT_DIR, '_batch_summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f'\n📋 Summary saved: {summary_path}')
    print(f'✅ Batch OCR phase complete. Run inject_ocr_tests.py next.')


if __name__ == '__main__':
    main()
