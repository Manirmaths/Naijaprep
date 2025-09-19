# seed_questions.py
import csv
from pathlib import Path
from app import app, db
from app.models import Question, UserResponse

def norm_choice(x):
    """Coerce answer key to a single letter A/B/C/D."""
    if x is None:
        return "A"
    s = str(x).strip().upper()
    if s.startswith("OPTION "):
        s = s.replace("OPTION ", "", 1).strip()
    return s[0] if s and s[0] in "ABCD" else "A"

# Resolve CSV path robustly
BASE_DIR = Path(__file__).resolve().parent       # repo root if file at root
CANDIDATES = [
    BASE_DIR / "questions3.csv",
    BASE_DIR / "data" / "questions3.csv",       # fallback if you move it later
]
CSV_PATH = next((p for p in CANDIDATES if p.exists()), None)

if CSV_PATH is None:
    raise FileNotFoundError(
        f"Could not find questions CSV in any of: {', '.join(str(p) for p in CANDIDATES)}"
    )

with app.app_context():
    # If you want idempotent seed (don’t wipe prod attempts), comment these two lines:
    db.session.query(UserResponse).delete()
    db.session.query(Question).delete()
    db.session.commit()

    inserted = 0
    with CSV_PATH.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            q = Question(
                topic=row["topic"].strip(),
                difficulty=int(row["difficulty"]),
                question_text=row["question_text"].strip(),
                option_a=row["option_a"].strip(),
                option_b=row["option_b"].strip(),
                option_c=row["option_c"].strip(),
                option_d=row["option_d"].strip(),
                correct_option=norm_choice(row.get("correct_option")),
                explanation=(row.get("explanation") or "").strip(),
                exam_year=(row.get("exam_year") or None),
            )
            db.session.add(q)
            inserted += 1
        db.session.commit()

    print(f"✅ Seeded {Question.query.count()} questions from {CSV_PATH.name} (inserted {inserted}).")
