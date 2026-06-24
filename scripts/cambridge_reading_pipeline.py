#!/usr/bin/env python3
"""Full Cambridge IELTS reading importer for Cambridge 1-3.

The importer reads the whole source book, segments Academic Reading by
READING PASSAGE anchors, classifies the original question sections into a
small schema, and replaces existing Cambridge 1/2/3 entries in the local
reading test database.
"""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import re
import subprocess
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "reading_tests.json"
API_PATH = PROJECT_ROOT / "api" / "reading-tests.json"
REPORT_PATH = PROJECT_ROOT / "scripts" / "ocr_output" / "cambridge_reading_report.json"

LIBRARY_ROOT = Path("/Users/zzzzhangjintao/Desktop/IELTS_Organized_Library/01_剑桥真题系列_Official_Mocks")
SOURCE_FILES = {
    1: LIBRARY_ROOT / "Cam_1" / "【1】剑桥雅思真题1.pdf",
    2: LIBRARY_ROOT / "Cam_2" / "【2】剑桥雅思真题2.pdf",
    3: LIBRARY_ROOT / "Cam_3" / "【3】剑桥雅思真题3.pdf",
}


CAM3_SPECS = [
    {
        "test": 1,
        "passages": [
            {
                "passage": 1,
                "title": "The Rocket: From East to West",
                "topic": "History",
                "answers": ["iv", "i", "v", "vii", "B", "D", "A", "A", "B", "E", "B", "E", "F", "G"],
            },
            {
                "passage": 2,
                "title": "The Risks of Cigarette Smoke",
                "topic": "Science",
                "start": 15,
                "answers": ["B", "A", "C", "NO", "NOT GIVEN", "YES", "NOT GIVEN", "E", "G", "H", "A", "B", "B", "C"],
            },
            {
                "passage": 3,
                "title": "The Scientific Method",
                "topic": "Science",
                "start": 29,
                "answers": ["iv", "vii", "iii", "v", "vi", "B", "F", "YES", "NO", "NOT GIVEN", "YES", "D"],
            },
        ],
    },
    {
        "test": 2,
        "passages": [
            {
                "passage": 1,
                "title": "A Remarkable Beetle",
                "topic": "Environment",
                "answers": [
                    "NOT GIVEN",
                    "NO",
                    "YES",
                    "YES",
                    "NO",
                    "South African",
                    "French",
                    "Spanish",
                    "temperate",
                    "early spring",
                    "two to five",
                    "sub-tropical",
                    "South African tunneling species",
                ],
            },
            {
                "passage": 2,
                "title": "The Impact of Modern Farming",
                "topic": "Environment",
                "start": 14,
                "answers": ["v", "vii", "ii", "iv", "i", "G", "C", "F", "B", "C", "B", "D", "C", "A", "A"],
            },
            {
                "passage": 3,
                "title": "Role Set",
                "topic": "Sociology",
                "start": 29,
                "answers": ["NOT GIVEN", "YES", "YES", "NOT GIVEN", "YES", "NO", "NO", "role sign", "ritual", "role sign", "role set", "C"],
            },
        ],
    },
    {
        "test": 3,
        "passages": [
            {
                "passage": 1,
                "title": "The Department of Ethnography",
                "topic": "History",
                "answers": ["FALSE", "FALSE", "FALSE", "NOT GIVEN", "TRUE", "TRUE", "TS", "AT", "FA", "AT", "FA", "SE"],
            },
            {
                "passage": 2,
                "title": "Secrets of the Forest",
                "topic": "Environment",
                "start": 13,
                "answers": ["v", "i", "vi", "NO", "YES", "NOT GIVEN", "NO", "YES", "YES", "C", "A", "B", "C"],
            },
            {
                "passage": 3,
                "title": "The Effects of Light on Plant and Animal Species",
                "topic": "Science",
                "start": 26,
                "answers": ["A", "B", "B", "NOT GIVEN", "FALSE", "FALSE", "TRUE", "TRUE", "NOT GIVEN", "B", "D", "E", "B", "A", "F"],
            },
        ],
    },
    {
        "test": 4,
        "passages": [
            {
                "passage": 1,
                "title": "Air Pollution",
                "topic": "Environment",
                "answers": ["Los Angeles", "London", "Singapore", "London", "Los Angeles", "YES", "YES", "NO", "NO", "NO", "A", "D", "C"],
            },
            {
                "passage": 2,
                "title": "Votes for Women",
                "topic": "History",
                "start": 14,
                "answers": ["C", "D", "D and E", "advertising space", "colour scheme", "the Woman's Exhibition", "NO", "YES", "NO", "NO", "NOT GIVEN", "YES", "YES", "D"],
            },
            {
                "passage": 3,
                "title": "Measuring Organisational Performance",
                "topic": "Economics",
                "start": 28,
                "answers": ["A", "C", "C", "supervision", "productivity", "reduced", "leadership", "overstaffed", "reduced", "C", "D", "G", "F"],
            },
        ],
    },
]


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pdftotext(pdf_path: Path) -> str:
    result = subprocess.run(["pdftotext", str(pdf_path), "-"], check=True, capture_output=True, text=True)
    return normalize_text(result.stdout)


def normalize_text(text: str) -> str:
    replacements = {
        "\r\n": "\n",
        "\r": "\n",
        "": "'",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "—": "-",
        "–": "-",
        "ﬁ": "fi",
        "ﬂ": "fl",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    lines = []
    for raw in text.splitlines():
        line = re.sub(r"[ \t]+", " ", raw.strip())
        if line in {"Reading", "Rreading"}:
            continue
        lines.append(line)
    return "\n".join(lines)


def extract_academic_reading_region(text: str, book: int) -> str:
    if book in {1, 3}:
        start_hint = re.search(r"\f(?:Practice\s+)?Test\s+1\b", text, re.I)
        start_pos = start_hint.end() if start_hint else 0
        start = text.find("READING PASSAGE 1", start_pos)
    else:
        start = text.find("READING PASSAGE 1")
    if start < 0:
        raise ValueError(f"Cambridge {book}: no READING PASSAGE 1 anchor found")
    end = text.find("\fAnswer key", start)
    if end < 0:
        end = text.find("\nAnswer key", start)
    if end < 0:
        end = len(text)
    return text[start:end]


def segment_passages(text: str, book: int) -> list[str]:
    if book == 2:
        region = extract_academic_reading_region(text, book)
        specs = specs_for_book(2)
        markers = []
        previous_idx = 0
        for test in specs:
            for passage in test["passages"]:
                marker = passage["marker"]
                idx = region.find(marker)
                if idx == -1:
                    raise ValueError(f"Cambridge 2: missing passage marker {marker!r}")
                qstart = int(passage.get("start", 1))
                q_anchor_re = re.compile(rf"Questions?\s+{qstart}\b", re.I)
                q_anchors = [m.start() for m in q_anchor_re.finditer(region, previous_idx, idx)]
                start_idx = q_anchors[-1] if q_anchors else idx
                markers.append((start_idx, passage))
                previous_idx = idx
        markers.sort(key=lambda item: item[0])
        chunks_by_marker = {}
        for i, (idx, passage) in enumerate(markers):
            end = markers[i + 1][0] if i + 1 < len(markers) else len(region)
            if end == -1:
                end = len(region)
            chunks_by_marker[passage["marker"]] = region[idx:end].strip()
        return [chunks_by_marker[passage["marker"]] for test in specs for passage in test["passages"]]

    region = extract_academic_reading_region(text, book)
    matches = list(re.finditer(r"^READING PASSAGE\s+([123])\s*$", region, re.M | re.I))
    if len(matches) < 12:
        raise ValueError(f"Cambridge {book}: expected 12 reading passages, found {len(matches)}")
    chunks = []
    for i, match in enumerate(matches[:12]):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(region)
        chunks.append(region[match.start():end].strip())
    return chunks


def split_body_and_questions(chunk: str, passage: dict[str, Any] | None = None) -> tuple[str, str]:
    if passage and passage.get("marker") and passage["marker"] in chunk:
        marker_idx = chunk.find(passage["marker"])
        next_questions = re.search(r"\n\s*Questions?\s+\d", chunk[marker_idx + len(passage["marker"]):], re.I)
        body_end = marker_idx + len(passage["marker"]) + next_questions.start() if next_questions else len(chunk)
        body = chunk[marker_idx:body_end].strip()
        qtext = chunk.strip()
        return body, qtext

    q_match = re.search(r"\n\s*Questions?\s+\d", chunk, re.I)
    if not q_match:
        return chunk, ""
    body = chunk[: q_match.start()].strip()
    qtext = chunk[q_match.start():].strip()
    if passage and len(re.findall(r"[A-Za-z]+", body)) < 80:
        recovered = recover_body_after_front_questions(chunk, passage["title"])
        if recovered:
            body = recovered
    return body, qtext


def recover_body_after_front_questions(chunk: str, title: str) -> str:
    title_words = [w.upper() for w in re.findall(r"[A-Za-z]+", title) if len(w) > 3]
    candidates = []
    lines = chunk.splitlines()
    offsets = []
    offset = 0
    for line in lines:
        offsets.append(offset)
        offset += len(line) + 1
    for idx, line in enumerate(lines):
        window = lines[idx: idx + 4]
        upper = " ".join(window).upper()
        score = sum(1 for word in title_words if word in upper)
        looks_like_title = any(
            len(re.findall(r"[A-Za-z]", item)) > 2
            and len(re.findall(r"[A-Z]", item)) / max(1, len(re.findall(r"[A-Za-z]", item))) > 0.75
            for item in window
        )
        if score >= max(1, min(2, len(title_words))):
            if looks_like_title:
                candidates.append(offsets[idx])
    if not candidates:
        return ""
    start = candidates[0]
    rest = chunk[start:]
    next_q = re.search(r"\n\s*Questions?\s+\d", rest, re.I)
    if next_q and next_q.start() > 500:
        rest = rest[: next_q.start()]
    return rest.strip()


def paragraphs_from_body(body: str, title: str) -> str:
    body = re.sub(r"READING PASSAGE\s+\d+", "", body, flags=re.I)
    body = re.sub(r"You should spend about 20 minutes.*?(?:below\.?|pages?\.?)", "", body, flags=re.I | re.S)
    body = re.sub(r"\n\s*the following pages?\.?", "", body, flags=re.I)
    body = re.sub(re.escape(title), "", body, count=1, flags=re.I)
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    paras: list[str] = []
    current: list[str] = []
    for line in lines:
        if re.fullmatch(r"\d+", line):
            continue
        if re.fullmatch(r"[A-J]", line):
            if current:
                paras.append(" ".join(current))
            current = [line]
            continue
        if re.match(r"^[A-J]\s+", line) and current:
            paras.append(" ".join(current))
            current = [line]
            continue
        if current and len(" ".join(current)) > 520 and not re.match(r"^[a-z,;:)\]]", line):
            paras.append(" ".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        paras.append(" ".join(current))
    cleaned = []
    for para in paras:
        para = re.sub(r"\s+", " ", para).strip()
        if len(para) > 24:
            cleaned.append(f"<p>{html.escape(para, quote=False)}</p>")
    return "\n".join(cleaned)


def question_sections(qtext: str) -> list[dict[str, Any]]:
    pattern = re.compile(r"Questions?\s+(\d+)\s*(?:(?:-|and|to)\s*(\d+))?", re.I)
    matches = list(pattern.finditer(qtext))
    sections = []
    for i, match in enumerate(matches):
        start = int(match.group(1))
        end = int(match.group(2) or start)
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(qtext)
        sections.append({"start": start, "end": end, "text": qtext[match.start():body_end].strip()})
    return sections


def section_for_question(sections: list[dict[str, Any]], qnum: int, qtext: str) -> dict[str, Any]:
    for sec in sections:
        if sec["start"] <= qnum <= sec["end"]:
            return sec
    return {"start": qnum, "end": qnum, "text": qtext[:1200]}


def infer_question_type(answer: str, section: str) -> str:
    upper_answer = answer.upper().strip()
    upper_section = section.upper()
    roman = re.fullmatch(r"[ivx]+", answer.strip(), re.I)
    identifying = {"TRUE", "FALSE", "YES", "NO", "NOT GIVEN"}
    if upper_answer in identifying:
        return "IDENTIFYING"
    if roman or "LIST OF HEADINGS" in upper_section or "MATCH EACH" in upper_section or "MATCHING" in upper_section:
        return "MATCHING"
    if re.fullmatch(r"[A-Z](?:\s*(?:AND|,|/)\s*[A-Z])?", upper_answer):
        if "CHOOSE THE CORRECT LETTER" in upper_section or "CHOOSE THE APPROPRIATE LETTER" in upper_section:
            return "CHOICE"
        if "MATCH" in upper_section or "WHICH PARAGRAPH" in upper_section or "LIST OF" in upper_section or "FOLLOWING" in upper_section:
            return "MATCHING"
        return "CHOICE"
    return "COMPLETION"


def extract_options(section: str, qtype: str) -> list[dict[str, str]]:
    options: list[dict[str, str]] = []
    seen = set()
    option_source = section
    if "List of Headings" in section:
        option_source = section.split("List of Headings", 1)[1]
        option_source = re.split(r"\n\s*(?:Example|Questions?\s+\d|\d+\s+[A-Z]|[A-Z]\s+[A-Z])\b", option_source, maxsplit=1)[0]
    if qtype == "MATCHING":
        option_re = re.compile(r"^\s*([A-Z]{1,3}|[ivx]{1,5})\s+(.{2,160})$", re.M)
    else:
        option_re = re.compile(r"^\s*([A-D])\s+(.{2,160})$", re.M)
    for code, label in option_re.findall(option_source):
        code = code.strip()
        label = re.sub(r"\s+", " ", label).strip()
        if code.upper() in {"READING", "QUESTIONS"} or len(label) < 2 or len(code) > 4:
            continue
        if qtype == "MATCHING" and re.fullmatch(r"[A-Z]{2,3}", code) and len(label.split()) > 12:
            continue
        key = (code.lower(), label.lower())
        if key in seen:
            continue
        seen.add(key)
        options.append({"value": code, "label": label})
    if qtype == "MATCHING":
        lines = [line.strip() for line in option_source.splitlines() if line.strip()]
        for i, line in enumerate(lines[:-1]):
            if re.fullmatch(r"[ivx]{1,5}", line) and not any(o["value"].lower() == line.lower() for o in options):
                label = re.sub(r"\s+", " ", lines[i + 1]).strip()
                if len(label) > 2 and not re.fullmatch(r"[ivx]{1,5}|[A-Z]{1,3}", label):
                    options.append({"value": line, "label": label})
    return options[:20]


def prompt_for_question(section: str, qnum: int, title: str) -> str:
    lines = [line.strip() for line in section.splitlines() if line.strip()]
    captures: list[str] = []
    start_re = re.compile(rf"^{qnum}\s+(.+)")
    blank_re = re.compile(rf"\(?{qnum}\)?")
    for idx, line in enumerate(lines):
        if start_re.search(line) or blank_re.search(line):
            captures = lines[max(0, idx - 3): idx + 6]
            break
    if not captures:
        captures = lines[:12]
    text = re.sub(r"\s+", " ", " ".join(captures)).strip()
    if len(text) > 700:
        text = text[:697].rsplit(" ", 1)[0] + "..."
    return f"{title} - Q{qnum}: {text}"


def normalize_answer(answer: str) -> str:
    return re.sub(r"\s+", " ", str(answer)).strip()


def answer_options_for_identifying(answer: str) -> tuple[list[str], int | str]:
    upper = answer.upper()
    if upper in {"YES", "NO"}:
        return ["YES", "NO", "NOT GIVEN"], {"YES": 0, "NO": 1, "NOT GIVEN": 2}[upper]
    if upper == "NOT GIVEN":
        return ["TRUE", "FALSE", "NOT GIVEN"], 2
    return ["TRUE", "FALSE", "NOT GIVEN"], {"TRUE": 0, "FALSE": 1, "NOT GIVEN": 2}[upper]


def build_questions(qtext: str, passage: dict[str, Any]) -> list[dict[str, Any]]:
    start = int(passage.get("start", 1))
    sections = question_sections(qtext)
    questions = []
    for offset, raw_answer in enumerate(passage["answers"]):
        qnum = start + offset
        answer = normalize_answer(raw_answer)
        sec = section_for_question(sections, qnum, qtext)
        sec_text = sec["text"]
        qtype = infer_question_type(answer, sec_text)
        item: dict[str, Any] = {
            "id": qnum,
            "type": qtype,
            "legacyType": {"IDENTIFYING": "true_false_not_given", "COMPLETION": "short_answer"}.get(qtype, qtype.lower()),
            "questionText": prompt_for_question(sec_text, qnum, passage["title"]),
            "correctAnswer": answer,
            "sectionRange": [sec["start"], sec["end"]],
        }
        if qtype == "IDENTIFYING":
            options, correct = answer_options_for_identifying(answer)
            item["options"] = options
            item["correctAnswer"] = correct
            item["answerText"] = answer
        elif qtype in {"CHOICE", "MATCHING"}:
            item["options"] = extract_options(sec_text, qtype)
            item["answerText"] = answer
            if qtype == "MATCHING":
                item["matching"] = {
                    "prompt": re.sub(r"\s+", " ", sec_text[:500]).strip(),
                    "options": item["options"],
                }
        else:
            item["wordLimit"] = 3
            item["completionText"] = prompt_for_question(sec_text, qnum, passage["title"])
        questions.append(item)
    return questions


def word_count_from_html(passage_html: str) -> int:
    text = re.sub(r"<[^>]+>", " ", passage_html)
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?", html.unescape(text)))


def difficulty(word_count: int) -> int:
    if word_count < 650:
        return 2
    if word_count < 850:
        return 3
    return 4


def specs_for_book(book: int) -> list[dict[str, Any]]:
    if book == 1:
        return load_module(PROJECT_ROOT / "scripts" / "import_cambridge1.py", "cam1_import").TEST_SPECS
    if book == 2:
        return load_module(PROJECT_ROOT / "scripts" / "import_cambridge2.py", "cam2_import").TEST_SPECS
    if book == 3:
        return CAM3_SPECS
    raise ValueError(book)


def build_entries_for_book(book: int) -> list[dict[str, Any]]:
    pdf_path = SOURCE_FILES[book]
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)
    text = pdftotext(pdf_path)
    chunks = segment_passages(text, book)
    specs = specs_for_book(book)
    passage_specs = [passage for test in specs for passage in test["passages"]]
    if len(passage_specs) != 12:
        raise ValueError(f"Cambridge {book}: expected 12 specs, found {len(passage_specs)}")

    entries = []
    for index, (passage, chunk) in enumerate(zip(passage_specs, chunks)):
        test_no = specs[index // 3]["test"]
        body, qtext = split_body_and_questions(chunk, passage)
        passage_html = paragraphs_from_body(body, passage["title"])
        questions = build_questions(qtext, passage)
        wc = word_count_from_html(passage_html)
        entries.append(
            {
                "id": f"cam{book}-test{test_no}-passage{passage['passage']}",
                "title": passage["title"],
                "topic": passage["topic"],
                "category": "Official Cambridge Mocks (官方真题)",
                "source": f"Cambridge {book} - Test {test_no} Passage {passage['passage']}",
                "main_class": "Official Cambridge Mocks (官方真题)",
                "difficulty": difficulty(wc),
                "totalTime": 1200,
                "wordCount": wc,
                "questionCount": len(questions),
                "schemaVersion": 2,
                "passageText": passage_html,
                "questions": questions,
            }
        )
    return entries


def validate_entries(entries: list[dict[str, Any]], book: int) -> dict[str, Any]:
    tests: dict[int, list[dict[str, Any]]] = {}
    for entry in entries:
        match = re.search(r"Test\s+(\d+)", entry["source"])
        tests.setdefault(int(match.group(1)), []).append(entry)
    problems = []
    warnings = []
    for test_no in range(1, 5):
        group = tests.get(test_no, [])
        if len(group) != 3:
            problems.append(f"Cambridge {book} Test {test_no}: expected 3 passages, got {len(group)}")
        q_total = sum(item["questionCount"] for item in group)
        if q_total != 40 and book != 1:
            problems.append(f"Cambridge {book} Test {test_no}: expected 40 questions, got {q_total}")
        elif q_total != 40:
            warnings.append(f"Cambridge {book} Test {test_no}: source book has {q_total} reading questions")
    type_counts: dict[str, int] = {}
    for entry in entries:
        for question in entry["questions"]:
            type_counts[question["type"]] = type_counts.get(question["type"], 0) + 1
    return {
        "book": book,
        "passages": len(entries),
        "questions": sum(entry["questionCount"] for entry in entries),
        "typeCounts": type_counts,
        "problems": problems,
        "warnings": warnings,
    }


def write_database(new_entries: list[dict[str, Any]], dry_run: bool) -> None:
    db = json.loads(DB_PATH.read_text())
    replace_ids = {entry["id"] for entry in new_entries}
    replace_books = {int(re.match(r"cam(\d+)-", entry["id"]).group(1)) for entry in new_entries}
    filtered = []
    for test in db["tests"]:
        tid = str(test.get("id", ""))
        src = str(test.get("source", ""))
        should_replace = tid in replace_ids or any(tid.startswith(f"cam{book}-test") or f"Cambridge {book} " in src for book in replace_books)
        if not should_replace:
            filtered.append(test)
    db["tests"] = filtered + new_entries
    if dry_run:
        return
    for path in (DB_PATH, API_PATH):
        path.write_text(json.dumps(db, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--books", nargs="+", type=int, default=[1, 2, 3], choices=[1, 2, 3])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    all_entries: list[dict[str, Any]] = []
    report = []
    for book in args.books:
        entries = build_entries_for_book(book)
        summary = validate_entries(entries, book)
        report.append(summary)
        if summary["problems"]:
            raise SystemExit("\n".join(summary["problems"]))
        for warning in summary["warnings"]:
            print(f"WARNING: {warning}")
        all_entries.extend(entries)
        print(f"Cambridge {book}: {summary['passages']} passages, {summary['questions']} questions, {summary['typeCounts']}")

    write_database(all_entries, args.dry_run)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    if args.dry_run:
        print("Dry run complete. Database not modified.")
    else:
        print(f"Updated {DB_PATH}")
        print(f"Updated {API_PATH}")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
