# seed_questions.py
import csv
import io
from pathlib import Path
from typing import List, Optional, Tuple

from sqlalchemy import inspect
import bleach  # ← make sure 'bleach' is installed

from app import create_app, db
from app.models import Question, UserResponse

# -----------------------------
# Configuration
# -----------------------------
REQUIRED_HEADERS = [
    "topic",
    "difficulty",
    "question_text",
    "option_a",
    "option_b",
    "option_c",
    "option_d",
    "correct_option",
    "explanation",
    "exam_year",
]

# Map CSV filenames -> subject value stored in DB
SUBJECT_STEMS = {
    "mathsQuestions": "Mathematics",
    "englishQuestions": "English",
    "physicsQuestions": "Physics",
    "chemistryQuestions": "Chemistry",
    "biologyQuestions": "Biology",
    "geographyQuestions": "Geography",
    "economicsQuestions": "Economics",
    "literatureQuestions": "Literature",
    "governmentQuestions": "Government",
    "commerceQuestions": "Commerce",
    "accountingQuestions": "Accounting",
}

# Encodings to try when reading CSVs
ENCODING_CANDIDATES = (
    "utf-8-sig",
    "utf-8",
    "cp1252",
    "latin-1",
    "utf-16",
    "utf-16-le",
    "utf-16-be",
)

# ---- HTML sanitization allowlist ----
ALLOWED_TAGS = {
    # basic text
    "b", "strong", "i", "em", "u", "br", "p", "span", "div",
    "sub", "sup", "ul", "ol", "li", "blockquote", "code", "pre",
    # tables if needed in explanations
    "table", "thead", "tbody", "tr", "th", "td",
    # keep images OFF by default; add "img" if you really need it (then also whitelist src)
}
ALLOWED_ATTRS = {
    "*": ["class", "style"],  # keep minimal styling if you must; or drop "style" to be stricter
}
ALLOWED_STYLES = [
    # keep empty for stricter setup; or allow limited inline styles if you trust the source
]

def sanitize_html(s: Optional[str]) -> str:
    if not s:
        return ""
    # strip=True drops disallowed tags entirely (instead of escaping them)
    return bleach.clean(s, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, styles=ALLOWED_STYLES, strip=True)


def filename_to_subject(csv_path: Path) -> Optional[str]:
    """Map file stem -> subject."""
    return SUBJECT_STEMS.get(csv_path.stem)


def ensure_subject_column():
    """
    Add Question.subject column if missing (SQLAlchemy 2.x safe).
    Uses inspector to check columns, then runs a simple ALTER TABLE.
    """
    engine = db.engine
    insp = inspect(engine)
    try:
        col_names = [c["name"] for c in insp.get_columns("question")]
    except Exception:
        # Table might not exist yet; let SQLAlchemy create it via app init/migrations.
        return

    if "subject" in col_names:
        return

    ddl = "ALTER TABLE question ADD COLUMN subject VARCHAR(255)"
    try:
        with engine.begin() as conn:
            conn.exec_driver_sql(ddl)
    except Exception:
        # Best-effort: ignore if already added by a race or different migration path
        pass


def find_csv_files(base_dir: Path) -> List[Path]:
    """
    Resolve CSV paths:
      - data/*.csv (alphabetical order)
      - questions3.csv in root (legacy)
      - data/questions3.csv (legacy)
    """
    data_dir = base_dir / "data"
    found: List[Path] = []

    if data_dir.exists():
        for p in sorted(data_dir.glob("*.csv")):
            found.append(p)

    root_q = base_dir / "questions3.csv"
    data_q = data_dir / "questions3.csv"
    for p in (root_q, data_q):
        if p.exists():
            found.append(p)

    # Dedup while preserving order
    uniq = []
    seen = set()
    for p in found:
        rp = p.resolve()
        if rp not in seen:
            uniq.append(p)
            seen.add(rp)
    return uniq


def decode_entire_file(csv_path: Path) -> Tuple[str, str]:
    """
    Read raw bytes, then try to decode the entire file using candidate encodings.
    Validates headers exist.
    """
    raw = csv_path.read_bytes()
    tried = []

    for enc in ENCODING_CANDIDATES:
        try:
            text_data = raw.decode(enc)
            reader = csv.DictReader(io.StringIO(text_data))
            if not reader.fieldnames:
                tried.append(f"{enc} (no headers found)")
                continue
            missing = [h for h in REQUIRED_HEADERS if h not in reader.fieldnames]
            if missing:
                tried.append(f"{enc} (missing headers: {missing})")
                continue
            return text_data, enc
        except Exception as e:
            tried.append(f"{enc} ({e.__class__.__name__}: {e})")

    raise UnicodeError(
        f"Could not read {csv_path.name} with any encoding. Tried: " + "; ".join(tried)
    )


def to_int(s: Optional[str], default: int = 1) -> int:
    try:
        return int(str(s).strip())
    except Exception:
        return default


def main():
    base_dir = Path(__file__).resolve().parent
    csv_files = find_csv_files(base_dir)

    if not csv_files:
        raise FileNotFoundError(
            "No CSV files found. Put CSVs in ./data/ (e.g., mathsQuestions.csv) or add questions3.csv in project root."
        )

    app = create_app()
    with app.app_context():
        ensure_subject_column()

        # Fresh seed
        db.session.query(UserResponse).delete()
        db.session.query(Question).delete()
        db.session.commit()
        print("✅ Database cleared. Reseeding…")

        grand_inserted = 0
        per_file_counts = []

        for csv_path in csv_files:
            try:
                text_data, encoding_used = decode_entire_file(csv_path)
            except Exception as e:
                print(f"❌ Skipping {csv_path.name}: {e}")
                continue

            csv_subject = filename_to_subject(csv_path)  # None for mixed legacy
            inserted = 0
            reader = csv.DictReader(io.StringIO(text_data))

            for row in reader:
                topic_raw = (row.get("topic") or "").strip()
                difficulty = to_int(row.get("difficulty"), default=1)

                # ---- sanitize everything user-facing ----
                topic = sanitize_html(topic_raw)
                question_text = sanitize_html(row.get("question_text") or "")
                option_a = sanitize_html(row.get("option_a") or "")
                option_b = sanitize_html(row.get("option_b") or "")
                option_c = sanitize_html(row.get("option_c") or "")
                option_d = sanitize_html(row.get("option_d") or "")
                explanation = sanitize_html(row.get("explanation") or "")

                correct_option_raw = row.get("correct_option")
                correct_option = norm_choice(correct_option_raw)

                exam_year_raw = row.get("exam_year")
                exam_year = (exam_year_raw or None).strip() if exam_year_raw else None

                # Minimal validity
                if not question_text or not topic:
                    continue

                q = Question(
                    subject=csv_subject,
                    topic=topic,
                    difficulty=difficulty,
                    question_text=question_text,
                    option_a=option_a,
                    option_b=option_b,
                    option_c=option_c,
                    option_d=option_d,
                    correct_option=correct_option,
                    explanation=explanation,
                    exam_year=exam_year,
                )
                db.session.add(q)
                inserted += 1

            db.session.commit()
            grand_inserted += inserted
            per_file_counts.append((csv_path.name, inserted, encoding_used))
            print(f"✅ {csv_path.name}: inserted {inserted} (encoding: {encoding_used})")

        total_in_db = Question.query.count()
        print("\n-----------------------------")
        print("Import Summary")
        print("-----------------------------")
        for name, cnt, enc in per_file_counts:
            print(f"- {name}: {cnt} rows (encoding {enc})")
        print(f"= Total inserted this run: {grand_inserted}")
        print(f"= Questions now in DB:     {total_in_db}")


def norm_choice(x: Optional[str]) -> str:
    """Coerce answer key to A/B/C/D."""
    if not x:
        return "A"
    s = str(x).strip().upper()
    if s.startswith("OPTION "):
        s = s.replace("OPTION ", "", 1).strip()
    return s[0] if s and s[0] in "ABCD" else "A"


if __name__ == "__main__":
    main()
