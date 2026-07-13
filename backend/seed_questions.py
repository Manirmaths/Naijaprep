# backend/seed_questions.py
"""
Import ../data/passages.csv and ../data/questions.csv into the backend database.

Safe to re-run: upserts by business key (Passage.passage_id / Question.question_id),
so you can grow the question bank in batches over time without duplicating
existing rows or disturbing user history (UserResponse/QuizAttempt reference
Question.id, which stays stable once a row exists).
"""
import csv
import html
import io
from pathlib import Path

import bleach

from app.database import SessionLocal, Base, engine
from app.models import Question, Passage
from app.subjects import normalize_subject

QUESTION_REQUIRED = [
    "question_id", "subject", "topic", "difficulty", "question_text",
    "option_a", "option_b", "option_c", "option_d", "correct_option",
    "explanation", "source", "status",
]
PASSAGE_REQUIRED = ["passage_id", "subject", "passage_text"]

ENCODING_CANDIDATES = ("utf-8-sig", "utf-8", "cp1252", "latin-1", "utf-16")

ALLOWED_TAGS = {
    "b", "strong", "i", "em", "u", "br", "p", "span", "div",
    "sub", "sup", "ul", "ol", "li", "blockquote", "code", "pre",
    "table", "thead", "tbody", "tr", "th", "td",
}
ALLOWED_ATTRS = {"*": ["class", "style"]}

VALID_DIFFICULTY = {"easy", "medium", "hard"}
VALID_SOURCE = {"original", "past-question", "licensed"}
VALID_STATUS = {"active", "draft"}


def sanitize(s):
    # bleach.clean() both strips disallowed tags *and* HTML-entity-escapes any
    # remaining literal <, >, & so the result is safe to insert as raw HTML.
    # We don't do that here -- question_text/options/explanation are rendered
    # as plain text (React auto-escapes) or parsed as LaTeX by KaTeX, neither
    # of which is raw-HTML injection. So we unescape after cleaning: this
    # keeps the tag-stripping security benefit while preserving literal
    # characters like "&" that are meaningful inside LaTeX (e.g. matrix
    # column separators in \begin{pmatrix}...\end{pmatrix}).
    if not s:
        return ""
    cleaned = bleach.clean(s, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)
    return html.unescape(cleaned)


def norm_choice(x):
    if not x:
        return "A"
    s = str(x).strip().upper()
    if s.startswith("OPTION "):
        s = s.replace("OPTION ", "", 1).strip()
    return s[0] if s and s[0] in "ABCD" else "A"


def norm_enum(value, valid, default):
    v = (value or "").strip().lower()
    return v if v in valid else default


def decode_file(path: Path, required_headers: list[str]):
    raw = path.read_bytes()
    for enc in ENCODING_CANDIDATES:
        try:
            text = raw.decode(enc)
            reader = csv.DictReader(io.StringIO(text))
            if reader.fieldnames and all(h in reader.fieldnames for h in required_headers):
                return text, enc
        except Exception:
            continue
    raise UnicodeError(f"Could not decode {path.name} with a known encoding/header set.")


def seed_passages(db, data_dir: Path) -> set:
    """Upsert passages.csv by passage_id. Returns the full set of known passage_ids (old + new)."""
    path = data_dir / "passages.csv"
    if not path.exists():
        print("No passages.csv found, skipping.")
        return set()

    try:
        text, enc = decode_file(path, PASSAGE_REQUIRED)
    except Exception as e:
        print(f"Skipping passages.csv: {e}")
        return set()

    known = {pid for (pid,) in db.query(Passage.passage_id).all()}
    reader = csv.DictReader(io.StringIO(text))
    inserted = 0
    for row in reader:
        pid = (row.get("passage_id") or "").strip()
        passage_text = sanitize(row.get("passage_text") or "")
        if not pid or not passage_text:
            continue
        if pid in known:
            continue
        known.add(pid)
        db.add(Passage(
            passage_id=pid,
            subject=normalize_subject(row.get("subject")) or (row.get("subject") or "").strip() or None,
            title=(row.get("title") or "").strip() or None,
            passage_text=passage_text,
        ))
        inserted += 1
    db.commit()
    print(f"passages.csv: +{inserted} new (encoding {enc})")
    return known


def seed_questions(db, data_dir: Path, known_passage_ids: set):
    path = data_dir / "questions.csv"
    if not path.exists():
        print("No questions.csv found, skipping.")
        return

    try:
        text, enc = decode_file(path, QUESTION_REQUIRED)
    except Exception as e:
        print(f"Skipping questions.csv: {e}")
        return

    existing_ids = set()
    for (qid,) in db.query(Question.question_id).filter(Question.question_id.isnot(None)).all():
        existing_ids.add(qid)
    print(f"Upsert mode: {len(existing_ids)} questions already in DB (by question_id).")

    reader = csv.DictReader(io.StringIO(text))
    inserted = 0
    skipped = 0
    for row in reader:
        qid = (row.get("question_id") or "").strip()
        subject = normalize_subject(row.get("subject")) or (row.get("subject") or "").strip()
        topic = sanitize((row.get("topic") or "").strip())
        question_text = sanitize(row.get("question_text") or "")

        if not qid or not subject or not topic or not question_text:
            skipped += 1
            continue
        if qid in existing_ids:
            continue

        passage_id = (row.get("passage_id") or "").strip() or None
        if passage_id and passage_id not in known_passage_ids:
            print(f"  Warning: {qid} references unknown passage_id '{passage_id}' -- importing without the link.")
            passage_id = None

        existing_ids.add(qid)
        db.add(Question(
            question_id=qid,
            exam_type=(row.get("exam_type") or "").strip() or None,
            subject=subject,
            topic=topic,
            subtopic=sanitize((row.get("subtopic") or "").strip()) or None,
            difficulty=norm_enum(row.get("difficulty"), VALID_DIFFICULTY, "medium"),
            year=(row.get("year") or "").strip() or None,
            passage_id=passage_id,
            question_text=question_text,
            image_url=(row.get("image_url") or "").strip() or None,
            option_a=sanitize(row.get("option_a")),
            option_b=sanitize(row.get("option_b")),
            option_c=sanitize(row.get("option_c")),
            option_d=sanitize(row.get("option_d")),
            correct_option=norm_choice(row.get("correct_option")),
            explanation=sanitize(row.get("explanation")),
            tags=(row.get("tags") or "").strip() or None,
            source=norm_enum(row.get("source"), VALID_SOURCE, "original"),
            status=norm_enum(row.get("status"), VALID_STATUS, "active"),
        ))
        inserted += 1

    db.commit()
    total = db.query(Question).count()
    print(f"questions.csv: +{inserted} new, {skipped} skipped (missing a required field) (encoding {enc})")
    print(f"Total questions now in DB: {total}")


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    data_dir = Path(__file__).resolve().parent.parent / "data"

    known_passage_ids = seed_passages(db, data_dir)
    seed_questions(db, data_dir, known_passage_ids)

    db.close()


if __name__ == "__main__":
    main()
