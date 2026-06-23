#!/usr/bin/env python3
"""Import Cambridge IELTS 1 Academic Reading passages into reading_tests.json."""

import html
import json
import re
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "reading_tests.json"
PDF_PATH = Path(
    "/Users/zzzzhangjintao/Desktop/IELTS_Organized_Library/"
    "01_剑桥真题系列_Official_Mocks/Cam_1/【1】剑桥雅思真题1.pdf"
)


TEST_SPECS = [
    {
        "test": 1,
        "pages": (18, 40),
        "passages": [
            {
                "passage": 1,
                "title": "A spark, a flint: How fire leapt to life",
                "topic": "Technology",
                "answers": [
                    "preserve",
                    "unaware",
                    "chance",
                    "friction",
                    "rotating",
                    "percussion",
                    "Eskimos",
                    "despite",
                    "F",
                    "D",
                    "E",
                    "C",
                    "G",
                    "A",
                    "C",
                ],
            },
            {
                "passage": 2,
                "title": "Zoo conservation programmes",
                "topic": "Environment",
                "answers": [
                    "YES",
                    "YES",
                    "NOT GIVEN",
                    "NO",
                    "NO",
                    "NOT GIVEN",
                    "YES",
                    "B",
                    "C",
                    "A",
                    "A",
                    "D",
                    "E",
                ],
                "start": 16,
            },
            {
                "passage": 3,
                "title": "Architecture - Reaching for the Sky",
                "topic": "History",
                "answers": [
                    "timber and stone",
                    "Modernism",
                    "International style",
                    "badly designed buildings//multi-storey housing//mass-produced, low-cost high-rises",
                    "preservation",
                    "High-Tech",
                    "co-existence of styles//different styles together//styles mixed",
                    "G",
                    "F",
                    "H",
                    "C",
                    "D",
                ],
                "start": 29,
            },
        ],
    },
    {
        "test": 2,
        "pages": (40, 62),
        "passages": [
            {
                "passage": 1,
                "title": "Right and left-handedness in humans",
                "topic": "Science",
                "answers": ["B", "D", "C", "B", "A", "C", "E", "15-20%", "40%", "6%", "D", "B"],
            },
            {
                "passage": 2,
                "title": "Migratory beekeeping",
                "topic": "Environment",
                "answers": [
                    "prepare",
                    "full",
                    "smoke",
                    "charge",
                    "machines",
                    "combs",
                    "split",
                    "(hexagonal) cells//comb",
                    "frames (of comb)",
                    "screen",
                    "brood chamber",
                    "NOT GIVEN",
                    "YES",
                    "YES",
                    "NO",
                ],
                "start": 13,
            },
            {
                "passage": 3,
                "title": "Tourism",
                "topic": "Sociology",
                "answers": ["iii", "v", "iv", "vii", "viii", "NO", "YES", "NOT GIVEN", "YES", "NOT GIVEN", "D", "B", "F", "H"],
                "start": 28,
            },
        ],
    },
    {
        "test": 3,
        "pages": (60, 84),
        "passages": [
            {
                "passage": 1,
                "title": "Spoken corpus comes to life",
                "topic": "Education",
                "answers": ["vi", "ii", "x", "viii", "iv", "ix", "existing", "(related) phrases", "meanings//forms", "spoken//real//oral", "noise//pauses//noises and pauses", "B"],
            },
            {
                "passage": 2,
                "title": "Moles happy as homes go underground",
                "topic": "Technology",
                "answers": ["xi", "ix", "viii", "v", "i", "vii", "iii", "iv", "sell (more) quickly", "(South Limburg) planners", "(road/noise) embankments", "Olivetti employees", "adapt to", "his bakery business//a cool room"],
                "start": 13,
            },
            {
                "passage": 3,
                "title": "A Workaholic Economy",
                "topic": "Economics",
                "answers": ["NO", "NOT GIVEN", "YES", "NO", "YES", "NOT GIVEN", "C", "A", "B", "D", "F", "G"],
                "start": 27,
            },
        ],
    },
    {
        "test": 4,
        "pages": (81, 104),
        "passages": [
            {
                "passage": 1,
                "title": "Glass: Capturing the dance of light",
                "topic": "Technology",
                "answers": ["viii", "i", "ix", "iii", "vi", "molten glass//ribbon of glass//molten glass ribbon", "belt of steel//steel belt//moving belt", "(lightbulb) moulds", "A", "B", "A", "C", "A"],
            },
            {
                "passage": 2,
                "title": "Why some women cross the finish line ahead of men",
                "topic": "Sociology",
                "answers": ["E", "G", "A", "C", "F", "D", "A", "S", "M", "S", "(it has) doubled//doubling", "de-layering", "demographic trends", "employers"],
                "start": 14,
            },
            {
                "passage": 3,
                "title": "Population viability analysis",
                "topic": "Environment",
                "answers": ["YES", "NO", "NO", "NOT GIVEN", "vi", "iii", "i", "ii", "will/may not survive//will/may/could become extinct", "locality//distribution", "logging takes place/occurs", "B"],
                "start": 28,
            },
        ],
    },
]


def run_pdftotext(first_page, last_page):
    result = subprocess.run(
        ["pdftotext", "-f", str(first_page), "-l", str(last_page), str(PDF_PATH), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def clean_lines(text):
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            lines.append("")
            continue
        if line.isdigit():
            continue
        if line in {"Reading", "Rreading", "Practice Test 1", "Practice Test 2", "Practice Test 3", "Practice Test 4"}:
            continue
        if re.fullmatch(r"\f+", line):
            continue
        lines.append(re.sub(r"\s{2,}", " ", line))
    return "\n".join(lines)


def split_passages(test_text):
    start = re.search(r"^\s*READING PASSAGE\s+1\s*$", test_text, re.M)
    if not start:
        raise ValueError("No reading passage marker found")
    text = test_text[start.start():]
    text = re.split(r"\n\s*WRITING TASK\s+1\b", text, maxsplit=1, flags=re.I)[0]
    matches = list(re.finditer(r"^\s*READING PASSAGE\s+([123])\s*$", text, re.M))
    chunks = []
    for i, match in enumerate(matches[:3]):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunks.append(text[match.start():end])
    if len(chunks) != 3:
        raise ValueError(f"Expected 3 passages, found {len(chunks)}")
    return chunks


def split_body_and_questions(chunk, title):
    q_match = re.search(r"\n\s*Questions?\s+\d", chunk, re.I)
    if not q_match:
        raise ValueError(f"No question block found for {title}")
    body = chunk[: q_match.start()]
    qtext = chunk[q_match.start():]

    body = re.sub(r"READING PASSAGE\s+\d+", "", body, flags=re.I)
    body = re.sub(r"You should spend about 20 minutes.*?below\.?", "", body, flags=re.I | re.S)
    body = body.replace(title.upper(), title).replace(title, "", 1)
    return body.strip(), qtext.strip()


def paragraphs_from_body(body):
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    paras = []
    current = []
    for line in lines:
        if re.fullmatch(r"[A-I]", line):
            continue
        if re.match(r"^[A-I]\s+", line) and current:
            paras.append(" ".join(current))
            current = [line]
        elif current and (len(line) < 55 or re.match(r"^[A-I]\s+", line)):
            current.append(line)
        else:
            if current and len(" ".join(current)) > 260:
                paras.append(" ".join(current))
                current = []
            current.append(line)
    if current:
        paras.append(" ".join(current))

    cleaned = []
    for para in paras:
        para = re.sub(r"\s+", " ", para).strip()
        para = para.replace("", "'").replace("“", '"').replace("”", '"')
        if len(para) > 30:
            cleaned.append(f"<p>{html.escape(para, quote=False)}</p>")
    return "\n".join(cleaned)


def answer_to_question_type(answer):
    normalized = answer.upper()
    if normalized in {"YES", "NO", "NOT GIVEN"}:
        return "true_false_not_given", ["YES", "NO", "NOT GIVEN"], {"YES": 0, "NO": 1, "NOT GIVEN": 2}[normalized]
    if normalized in {"TRUE", "FALSE"}:
        return "true_false_not_given", ["TRUE", "FALSE", "NOT GIVEN"], {"TRUE": 0, "FALSE": 1, "NOT GIVEN": 2}[normalized]
    return "short_answer", None, answer


def section_instruction(qtext, question_number):
    pattern = re.compile(r"Questions?\s+(\d+)(?:\s*[-and]+\s*(\d+))?", re.I)
    sections = list(pattern.finditer(qtext))
    chosen = None
    for i, match in enumerate(sections):
        start = int(match.group(1))
        end = int(match.group(2) or start)
        if start <= question_number <= end:
            section_end = sections[i + 1].start() if i + 1 < len(sections) else len(qtext)
            chosen = qtext[match.start():section_end]
            break
    if not chosen:
        chosen = qtext[:1200]
    return chosen


def question_prompt(qtext, question_number, title):
    section = section_instruction(qtext, question_number)
    lines = [line.strip() for line in section.splitlines() if line.strip()]
    captures = []
    pattern_start = re.compile(rf"^{question_number}\s+(.*)")
    pattern_blank = re.compile(rf"\({question_number}\)")
    for idx, line in enumerate(lines):
        if pattern_start.search(line) or pattern_blank.search(line):
            captures = lines[max(0, idx - 3): idx + 6]
            break
    if not captures:
        captures = lines[:10]
    text = " ".join(captures)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 520:
        text = text[:517].rsplit(" ", 1)[0] + "..."
    return f"{title} - Q{question_number}: {text}"


def build_questions(qtext, passage_spec):
    start = passage_spec.get("start", 1)
    questions = []
    for offset, answer in enumerate(passage_spec["answers"]):
        qnum = start + offset
        qtype, options, correct = answer_to_question_type(answer)
        item = {
            "id": qnum,
            "type": qtype,
            "questionText": question_prompt(qtext, qnum, passage_spec["title"]),
            "correctAnswer": correct,
        }
        if options:
            item["options"] = options
        else:
            item["wordLimit"] = 3
        questions.append(item)
    return questions


def word_count_from_html(passage_html):
    text = re.sub(r"<[^>]+>", " ", passage_html)
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?", html.unescape(text)))


def difficulty(word_count):
    if word_count < 650:
        return 2
    if word_count < 850:
        return 3
    return 4


def build_entries():
    entries = []
    for test_spec in TEST_SPECS:
        raw = clean_lines(run_pdftotext(*test_spec["pages"]))
        chunks = split_passages(raw)
        for passage_spec, chunk in zip(test_spec["passages"], chunks):
            body, qtext = split_body_and_questions(chunk, passage_spec["title"])
            passage_html = paragraphs_from_body(body)
            questions = build_questions(qtext, passage_spec)
            wc = word_count_from_html(passage_html)
            entries.append(
                {
                    "id": f"cam1-test{test_spec['test']}-passage{passage_spec['passage']}",
                    "title": passage_spec["title"],
                    "topic": passage_spec["topic"],
                    "category": "Official Cambridge Mocks (官方真题)",
                    "source": f"Cambridge 1 - Test {test_spec['test']} Passage {passage_spec['passage']}",
                    "main_class": "Official Cambridge Mocks (官方真题)",
                    "difficulty": difficulty(wc),
                    "totalTime": 1200,
                    "wordCount": wc,
                    "questionCount": len(questions),
                    "passageText": passage_html,
                    "questions": questions,
                }
            )
    return entries


def main():
    if not PDF_PATH.exists():
        raise SystemExit(f"PDF not found: {PDF_PATH}")
    with DB_PATH.open() as f:
        db = json.load(f)
    tests = db["tests"]
    new_entries = build_entries()
    cam1_sources = {entry["source"] for entry in new_entries}
    tests = [test for test in tests if test.get("source") not in cam1_sources and not str(test.get("id", "")).startswith("cam1-test")]
    tests.extend(new_entries)
    db["tests"] = tests
    with DB_PATH.open("w") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Imported {len(new_entries)} Cambridge 1 passages into {DB_PATH}")
    print(f"Total tests: {len(tests)}")


if __name__ == "__main__":
    main()
