#!/usr/bin/env python3
"""
OCR Pipeline: Extract text from scanned IELTS reading PDFs.
Phase 1: Extract text via tesseract OCR (English + Chinese)
Phase 2: Structure into passage + questions JSON
Phase 3: Append to reading_tests.json
"""
import json
import os
import re
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract

# ── Config ──────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'scripts', 'ocr_output')
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'reading_tests.json')
DPI = 250  # Balance quality vs speed
LANG = 'eng+chi_sim'  # English + Simplified Chinese

# Priority PDFs (most likely to have readable text with questions)
PRIORITY_PDFS = [
    # 教主公开课 — 含真题展示 (lecture slides with real exam excerpts)
    {
        'path': '/Users/zzzzhangjintao/Desktop/IELTS_Organized_Library/02_阅读专项精读库_Reading_by_Topic/07_Reading_Methodology_and_Skills/教主阅读公开课/教主阅读公开课课件第3次  判断题和平行策略（含真题展示）.pdf',
        'label': '教主-判断+平行策略',
        'pages': 'all',
    },
    {
        'path': '/Users/zzzzhangjintao/Desktop/IELTS_Organized_Library/02_阅读专项精读库_Reading_by_Topic/07_Reading_Methodology_and_Skills/教主阅读公开课/教主阅读公开课课件第2次  顺序原则和平行策略（含真题展示）1.pdf',
        'label': '教主-顺序+平行策略',
        'pages': 'all',
    },
    {
        'path': '/Users/zzzzhangjintao/Desktop/IELTS_Organized_Library/02_阅读专项精读库_Reading_by_Topic/07_Reading_Methodology_and_Skills/教主阅读公开课/教主阅读公开课课件第5次 判断题，切水果，配对题平行策略（含真题展示）.pdf',
        'label': '教主-判断+配对平行策略',
        'pages': 'all',
    },
    {
        'path': '/Users/zzzzhangjintao/Desktop/IELTS_Organized_Library/02_阅读专项精读库_Reading_by_Topic/07_Reading_Methodology_and_Skills/教主阅读公开课/教主阅读公开课课件第6次  判断题，配对题A 平行策略（含真题展示）.ppt.pdf',
        'label': '教主-判断+配对A',
        'pages': 'all',
    },
    {
        'path': '/Users/zzzzhangjintao/Desktop/IELTS_Organized_Library/02_阅读专项精读库_Reading_by_Topic/07_Reading_Methodology_and_Skills/教主阅读公开课/教主阅读公开课课件第7次.pdf',
        'label': '教主-第7次',
        'pages': 'all',
    },
]


def ocr_pdf(pdf_path, label, pages='all', max_pages=None):
    """OCR a single PDF, return extracted text per page."""
    print(f'\n{"="*60}')
    print(f'OCR: {label}')
    print(f'File: {pdf_path}')
    try:
        images = convert_from_path(pdf_path, dpi=DPI)
        total = len(images)
        print(f'  Pages: {total} @ {DPI} DPI')
    except Exception as e:
        print(f'  ERROR converting PDF: {e}')
        return []

    if pages == 'all':
        page_range = range(total)
    else:
        page_range = pages

    if max_pages and len(page_range) > max_pages:
        page_range = list(page_range)[:max_pages]

    results = []
    for i in page_range:
        if i >= total:
            break
        try:
            text = pytesseract.image_to_string(images[i], lang=LANG)
            text = text.strip()
            if text:
                results.append({'page': i + 1, 'text': text, 'chars': len(text)})
            # Progress indicator
            if (i + 1) % 10 == 0:
                print(f'  ... processed page {i+1}/{total}')
        except Exception as e:
            print(f'  ERROR on page {i+1}: {e}')

    print(f'  Extracted text from {len(results)}/{len(page_range)} pages')
    return results


def save_ocr_output(label, results):
    """Save raw OCR output for later processing."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    safe_label = re.sub(r'[^a-zA-Z0-9一-鿿_-]', '_', label)
    out_path = os.path.join(OUTPUT_DIR, f'{safe_label}.txt')

    with open(out_path, 'w', encoding='utf-8') as f:
        for r in results:
            f.write(f"\n{'='*60}\n")
            f.write(f"=== PAGE {r['page']} ({r['chars']} chars) ===\n")
            f.write(f"{'='*60}\n")
            f.write(r['text'])
            f.write('\n')

    # Also save JSON with structured data
    json_path = os.path.join(OUTPUT_DIR, f'{safe_label}.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f'  Saved: {out_path} ({sum(r["chars"] for r in results)} chars total)')
    return out_path


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_results = {}
    for pdf_info in PRIORITY_PDFS:
        if not os.path.exists(pdf_info['path']):
            print(f'SKIP (not found): {pdf_info["path"]}')
            continue
        results = ocr_pdf(
            pdf_info['path'],
            pdf_info['label'],
            pages=pdf_info.get('pages', 'all'),
            max_pages=pdf_info.get('max_pages'),
        )
        if results:
            out_path = save_ocr_output(pdf_info['label'], results)
            all_results[pdf_info['label']] = {
                'path': out_path,
                'pages': len(results),
                'total_chars': sum(r['chars'] for r in results),
            }

    print(f'\n{"="*60}')
    print(f'SUMMARY: OCR complete for {len(all_results)} PDFs')
    for label, info in all_results.items():
        print(f'  {label}: {info["pages"]} pages, {info["total_chars"]} chars')
    print(f'\nOutput in: {OUTPUT_DIR}')
    print(f'Now run Phase 2 to parse content into reading_tests.json format.')


if __name__ == '__main__':
    main()
