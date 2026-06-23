#!/usr/bin/env python3
"""Import Cambridge IELTS 2 Academic Reading passages into reading_tests.json."""

import html
import json
import re
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "reading_tests.json"
API_PATH = PROJECT_ROOT / "api" / "reading-tests.json"
PDF_PATH = Path(
    "/Users/zzzzhangjintao/Desktop/IELTS_Organized_Library/"
    "01_剑桥真题系列_Official_Mocks/Cam_2/【2】剑桥雅思真题2.pdf"
)


TEST_SPECS = [
    {
        "test": 1,
        "passages": [
            {
                "passage": 1,
                "marker": "AIRPORTS ON WATER",
                "title": "Airports on Water",
                "topic": "Technology",
                "answers": ["A", "A", "B", "C", "B", "runways and taxiways", "terminal building site", "sand", "stiff clay", "Lantau Island", "sea walls", "rainfall", "geotextile"],
            },
            {
                "passage": 2,
                "marker": "Changing our",
                "title": "Changing our Understanding of Health",
                "topic": "Sociology",
                "start": 14,
                "answers": ["viii", "ii", "iv", "ix", "vii", "1946", "(the) wealthy (members) (of) (society)", "social, economic, environmental", "(the) 1970s", "NOT GIVEN", "YES", "NO", "NO", "NOT GIVEN"],
            },
            {
                "passage": 3,
                "marker": "CHILDREN'S THINKING",
                "title": "Children's Thinking",
                "topic": "Education",
                "start": 28,
                "answers": ["CH", "MC", "MC", "SH", "SH", "MC", "HTK", "SH", "NOT GIVEN", "YES", "YES", "YES", "NO"],
            },
        ],
    },
    {
        "test": 2,
        "passages": [
            {
                "passage": 1,
                "marker": "IMPLEMENTING THE CYCLE",
                "title": "Implementing the Cycle of Success: A Case Study",
                "topic": "Economics",
                "answers": ["C", "A", "C", "B", "B", "benchmarking", "(a range of) service delivery", "(performance) measures", "productivity", "Take Charge", "feedback", "employee(s')//staff", "30 days"],
            },
            {
                "passage": 2,
                "marker": "The discovery that language",
                "title": "The Language Barrier",
                "topic": "Education",
                "start": 14,
                "answers": ["major consequences", "surveys", "sales literature", "Eastern Europe//Far East//Russia//Arab world//Latin America//French-speaking Africa", "C", "B", "C", "(industrial) training (schemes)", "translation services", "(part-time) language courses", "(technical) glossaries", "D", "A"],
            },
            {
                "passage": 3,
                "marker": "What Is a Port City?",
                "title": "What Is a Port City?",
                "topic": "History",
                "start": 27,
                "answers": ["ii", "i", "v", "vi", "D", "C", "F", "G", "NO", "YES", "NO", "YES", "NOT GIVEN", "YES"],
            },
        ],
    },
    {
        "test": 3,
        "passages": [
            {
                "passage": 1,
                "marker": "ABSENTEEISM IN NURSING",
                "title": "Absenteeism in Nursing: A Longitudinal Study",
                "topic": "Economics",
                "answers": ["NO", "NO", "NO", "YES", "NOT GIVEN", "NO", "YES", "(local) businesses", "(work/working) schedule//rostering//roster(s)", "excessive", "voluntary absence/absenteeism", "twenty//20", "communication"],
            },
            {
                "passage": 2,
                "marker": "There are now over 700",
                "title": "The Motor Car",
                "topic": "Environment",
                "start": 14,
                "answers": ["C", "F", "E", "H", "A", "D", "NOT GIVEN", "NO", "NOT GIVEN", "YES", "YES", "YES", "NO"],
            },
            {
                "passage": 3,
                "marker": "Students who want",
                "title": "Biometrics",
                "topic": "Technology",
                "start": 27,
                "answers": ["iv", "vii", "viii", "iii", "ii", "i", "x", "B", "B", "E", "A", "B", "D", "E"],
            },
        ],
    },
    {
        "test": 4,
        "passages": [
            {
                "passage": 1,
                "marker": "Green Wave",
                "title": "Green Wave Washes Over Mainstream Shopping",
                "topic": "Environment",
                "answers": ["YES", "NO", "YES", "NOT GIVEN", "NO", "NOT GIVEN", "B", "B", "C", "honesty and openness", "consumers", "armchair ethicals", "social record"],
            },
            {
                "passage": 2,
                "marker": "There is a great concern",
                "title": "The Harm that Picture Books Can Cause",
                "topic": "Education",
                "start": 14,
                "answers": ["D", "B", "D", "C", "NO", "YES", "YES", "NOT GIVEN", "F", "C", "J", "I", "C"],
            },
            {
                "passage": 3,
                "marker": "It has been called",
                "title": "The Human Genome Project",
                "topic": "Science",
                "start": 27,
                "answers": ["Apollo (space) programme", "(early) next century", "7,000", "disease", "muscular dystrophy", "cystic fibrosis", "D", "C", "B", "C", "D", "B", "A", "A"],
            },
        ],
    },
]


def run_pdftotext():
    result = subprocess.run(
        ["pdftotext", "-f", "1", "-l", "55", str(PDF_PATH), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def normalize_text(text):
    text = text.replace("", "'").replace("“", '"').replace("”", '"')
    lines = []
    for raw in text.splitlines():
        line = re.sub(r"\s{2,}", " ", raw.strip())
        if line and not line.isdigit() and line not in {"Reading", "Rreading"}:
            lines.append(line)
    return "\n".join(lines)


def passage_chunks(text):
    flat = text
    markers = []
    for test in TEST_SPECS:
        for passage in test["passages"]:
            idx = flat.find(passage["marker"])
            if idx == -1:
                raise ValueError(f"Missing marker: {passage['marker']}")
            markers.append((idx, test, passage))
    markers.sort(key=lambda item: item[0])
    chunks = {}
    for i, (idx, test, passage) in enumerate(markers):
        end = markers[i + 1][0] if i + 1 < len(markers) else flat.find("Answer key", idx)
        if end == -1:
            end = len(flat)
        chunks[(test["test"], passage["passage"])] = flat[idx:end]
    return chunks


def split_body_and_questions(chunk):
    q_match = re.search(r"\n\s*Questions?\s+\d", chunk, re.I)
    if not q_match:
        return chunk, ""
    return chunk[: q_match.start()], chunk[q_match.start():]


def paragraphs_from_body(body, title, marker):
    body = body.replace(marker, title, 1)
    body = re.sub(r"READ(?:I|l)NG PASSAGE\s+\d+", "", body, flags=re.I)
    body = re.sub(r"You should spend about 20 minutes.*?(?:below\.?|pages\.)", "", body, flags=re.I | re.S)
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    paras = []
    current = []
    for line in lines:
        if re.fullmatch(r"[A-J]", line):
            continue
        if re.match(r"^[A-J]\s+", line) and current:
            paras.append(" ".join(current))
            current = [line]
        elif current and len(" ".join(current)) > 420:
            paras.append(" ".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        paras.append(" ".join(current))
    cleaned = []
    seen_title = False
    for para in paras:
        para = re.sub(r"\s+", " ", para).strip()
        if not para:
            continue
        if not seen_title and title.lower() in para.lower():
            para = re.sub(re.escape(title), "", para, flags=re.I).strip()
            seen_title = True
        if len(para) > 30:
            cleaned.append(f"<p>{html.escape(para, quote=False)}</p>")
    return "\n".join(cleaned)


def answer_to_question_type(answer):
    normalized = answer.upper()
    if normalized in {"YES", "NO", "NOT GIVEN"}:
        return "true_false_not_given", ["YES", "NO", "NOT GIVEN"], {"YES": 0, "NO": 1, "NOT GIVEN": 2}[normalized]
    if normalized in {"TRUE", "FALSE", "NOT GIVEN"}:
        return "true_false_not_given", ["TRUE", "FALSE", "NOT GIVEN"], {"TRUE": 0, "FALSE": 1, "NOT GIVEN": 2}[normalized]
    return "short_answer", None, answer


def question_prompt(qtext, qnum, title):
    if not qtext:
        return f"{title} - Q{qnum}: Answer the original Cambridge 2 question."
    pattern = re.compile(rf"(?:^|\n)\s*{qnum}\s+(.+?)(?=(?:\n\s*{qnum + 1}\s+)|\Z)", re.S)
    match = pattern.search(qtext)
    if match:
        text = match.group(0)
    else:
        blank = re.search(rf"\({qnum}\)", qtext)
        if blank:
            start = max(0, blank.start() - 260)
            end = min(len(qtext), blank.end() + 260)
            text = qtext[start:end]
        else:
            text = f"Answer the original Cambridge 2 question {qnum}."
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 520:
        text = text[:517].rsplit(" ", 1)[0] + "..."
    return f"{title} - Q{qnum}: {text}"


def build_questions(qtext, passage):
    start = passage.get("start", 1)
    questions = []
    for offset, answer in enumerate(passage["answers"]):
        qnum = start + offset
        qtype, options, correct = answer_to_question_type(answer)
        item = {
            "id": qnum,
            "type": qtype,
            "questionText": question_prompt(qtext, qnum, passage["title"]),
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
    text = normalize_text(run_pdftotext())
    chunks = passage_chunks(text)
    entries = []
    for test in TEST_SPECS:
        for passage in test["passages"]:
            chunk = chunks[(test["test"], passage["passage"])]
            body, qtext = split_body_and_questions(chunk)
            passage_html = paragraphs_from_body(body, passage["title"], passage["marker"])
            questions = build_questions(qtext, passage)
            wc = word_count_from_html(passage_html)
            entries.append(
                {
                    "id": f"cam2-test{test['test']}-passage{passage['passage']}",
                    "title": passage["title"],
                    "topic": passage["topic"],
                    "category": "Official Cambridge Mocks (官方真题)",
                    "source": f"Cambridge 2 - Test {test['test']} Passage {passage['passage']}",
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
    new_entries = build_entries()
    ids = {entry["id"] for entry in new_entries}
    sources = {entry["source"] for entry in new_entries}
    tests = [
        test
        for test in db["tests"]
        if test.get("id") not in ids and test.get("source") not in sources and not str(test.get("id", "")).startswith("cam2-test")
    ]
    tests.extend(new_entries)
    db["tests"] = tests
    for path in (DB_PATH, API_PATH):
        with path.open("w") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
            f.write("\n")
    print(f"Imported {len(new_entries)} Cambridge 2 passages")
    print(f"Total tests: {len(tests)}")


if __name__ == "__main__":
    main()
